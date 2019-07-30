import singer
from singer import metrics, metadata, Transformer
from singer.bookmarks import set_currently_syncing

from tap_outreach.discover import discover

LOGGER = singer.get_logger()

STREAM_PATHS = {
    'stages': 'stages'
}

def get_bookmark(state, stream_name, default):
    return state.get('bookmarks', {}).get(stream_name, default)

def write_bookmark(state, stream_name, value):
    if 'bookmarks' not in state:
        state['bookmarks'] = {}
    state['bookmarks'][stream_name] = value
    singer.write_state(state)

def write_schema(stream):
    schema = stream.schema.to_dict()
    singer.write_schema(stream.tap_stream_id, schema, stream.key_properties)

def process_records(stream, mdata, max_modified, records):
    schema = stream.schema.to_dict()
    with metrics.record_counter(stream.tap_stream_id) as counter:
        for record in records:
            record_flat = {
                'id': record['id']
            }
            for prop, value in record['attributes'].items():
                record_flat[prop] = value

            if record_flat['updatedAt'] > max_modified:
                max_modified = record_flat['updatedAt']

            with Transformer() as transformer:
                record_typed = transformer.transform(record_flat,
                                                     schema,
                                                     mdata)
            singer.write_record(stream.tap_stream_id, record_typed)
            counter.increment()
        return max_modified

def sync_endpoint(client, catalog, state, start_date, stream, mdata):
    stream_name = stream.tap_stream_id
    last_datetime = get_bookmark(state, stream_name, start_date)

    LOGGER.info('{} - Syncing data since {}'.format(stream.tap_stream_id, last_datetime))

    write_schema(stream)

    count = 1000
    offset = 0
    has_more = True
    max_modified = last_datetime
    while has_more:
        query_params = {
            'filter[updatedAt]': '{}..inf'.format(last_datetime),
            'sort': 'updatedAt',
            'page[limit]': count,
            'page[offset]': offset
        }

        data = client.get(
            STREAM_PATHS[stream_name],
            params=query_params,
            endpoint=stream_name)
        records = data['data']

        if len(records) < count:
            has_more = False
        else:
            offset += count

        max_modified = process_records(stream, mdata, max_modified, records)

        write_bookmark(state, stream_name, max_modified)

def update_current_stream(state, stream_name=None):  
    set_currently_syncing(state, stream_name) 
    singer.write_state(state)

def sync(client, catalog, state, start_date):
    if not catalog:
        catalog = discover(client)
        selected_streams = catalog.streams
    else:
        selected_streams = catalog.get_selected_streams(state)

    for stream in selected_streams:
        mdata = metadata.to_map(stream.metadata)
        update_current_stream(state, stream.tap_stream_id)
        sync_endpoint(client, catalog, state, start_date, stream, mdata)

    update_current_stream(state)

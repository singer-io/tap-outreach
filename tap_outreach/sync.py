import singer
from singer import metrics, metadata, Transformer
from singer.bookmarks import set_currently_syncing

from tap_outreach.discover import discover

LOGGER = singer.get_logger()

STEAM_CONFIGS = {
    'accounts': {
        'url_path': 'accounts',
        'replication': 'incremental',
        'filter_field': 'updatedAt',
        'fks': [
            'creatorId',
            'ownerId',
            'updaterId'
        ]
    },
    'call_dispositions': {
        'url_path': 'callDispositions',
        'replication': 'incremental',
        'filter_field': 'updatedAt',
        'fks': ['creatorId']
    },
    'call_purposes': {
        'url_path': 'callPurposes',
        'replication': 'incremental',
        'filter_field': 'updatedAt',
        'fks': ['creatorId']
    },
    'calls': {
        'url_path': 'calls',
        'replication': 'incremental',
        'filter_field': 'updatedAt',
        'fks': [
            'callDispositionId',
            'callPurposeId',
            'opportunityId',
            'prospectId',
            'sequenceId',
            'sequenceStateId',
            'sequenceStepId',
            'taskId',
            'userId'
        ]
    },
    'content_categories': {
        'url_path': 'contentCategories',
        'replication': 'incremental',
        'filter_field': 'updatedAt',
        'fks': ['creatorId']
    },
    'duties': {
        'url_path': 'duties',
        'replication': 'full'
    },
    'events': {
        'url_path': 'events',
        'replication': 'incremental',
        'filter_field': 'eventAt',
        'fks': ['prospectId', 'userId']
    },
    'mailboxes': {
        'url_path': 'mailboxes',
        'replication': 'incremental',
        'filter_field': 'updatedAt',
        'fks': ['creatorId', 'updaterId']
    },
    'mailings': {
        'url_path': 'mailings',
        'replication': 'incremental',
        'filter_field': 'updatedAt',
        'fks': [
            'calendarId',
            'mailboxId',
            'opportunityId',
            'prospectId',
            'sequenceId',
            'sequenceStateId',
            'sequenceStepId',
            'taskId',
            'templateId'
        ]
    },
    'opportunities': {
        'url_path': 'opportunities',
        'replication': 'incremental',
        'filter_field': 'updatedAt',
        'fks': [
            'accountId',
            'creatorId',
            'opportunityStageId',
            'ownerId'
        ]
    },
    'personas': {
        'url_path': 'personas',
        'replication': 'incremental',
        'filter_field': 'updatedAt'
    },
    'prospects': {
        'url_path': 'prospects',
        'replication': 'incremental',
        'filter_field': 'updatedAt',
        'fks': [
            'accountId',
            'creatorId',
            'defaultPluginMappingId',
            'ownerId',
            'personaId',
            'stageId',
            'updaterId'
        ]
    },
    'stages': {
        'url_path': 'stages',
        'replication': 'incremental',
        'filter_field': 'updatedAt',
        'fks': ['creatorId', 'updaterId']
    },
    'tasks': {
        'url_path': 'tasks',
        'replication': 'incremental',
        'filter_field': 'updatedAt',
        'fks': [
            'accountId',
            'callId',
            'completerId',
            'creatorId',
            'mailingId',
            'opportunityId',
            'ownerId',
            'prospectId',
            'sequenceId',
            'sequenceStateId',
            'sequenceStepId',
            'subjectId',
            'taskPriorityId',
            'taskThemeId',
            'templateId'
        ]
    },
    'teams': {
        'url_path': 'teams',
        'replication': 'full',
        'fks': ['creatorId', 'updaterId']
    },
    'users': {
        'url_path': 'users',
        'replication': 'incremental',
        'filter_field': 'updatedAt',
        'fks': [
            'calendarId',
            'mailboxId',
            'profileId',
            'roleId',
            'creatorId',
            'updaterId'
        ]
    }
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

def process_records(stream, mdata, max_modified, records, filter_field, fks):
    schema = stream.schema.to_dict()
    with metrics.record_counter(stream.tap_stream_id) as counter:
        for record in records:
            record_flat = {
                'id': record['id']
            }
            for prop, value in record['attributes'].items():
                if prop == 'id':
                    raise Exception('Error flattening Outeach record - conflict with `id` key')
                record_flat[prop] = value

            if 'relationships' in record:
                for prop, value in record['relationships'].items():
                    if 'data' not in value and 'links' not in value:
                        raise Exception('Only `data` or `links` expected in relationships')

                    fk_field_name = '{}Id'.format(prop)

                    if 'data' in value and fk_field_name in fks:
                        data_value = value['data']
                        if data_value is not None and 'id' not in data_value:
                            raise Exception('null or `id` field expected for `data` relationship')

                        if fk_field_name in record_flat:
                            raise Exception(
                                '`{}` exists as both an attribute and generated relationship name'.format(fk_field_name))

                        if data_value == None:
                            record_flat[fk_field_name] = None
                        else:
                            record_flat[fk_field_name] = data_value['id']

            if filter_field in record_flat and record_flat[filter_field] > max_modified:
                max_modified = record_flat[filter_field]

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

    write_schema(stream)

    stream_config = STEAM_CONFIGS[stream_name]
    filter_field = stream_config.get('filter_field')
    fks = stream_config.get('fks', [])

    count = 1000
    offset = 0
    has_more = True
    max_modified = last_datetime
    paginate_datetime = last_datetime
    while has_more:
        query_params = {
            'page[limit]': count,
            'page[offset]': offset
        }

        if stream_config.get('replication') == 'incremental':
            query_params['filter[{}]'.format(filter_field)] = '{}..inf'.format(paginate_datetime)
            query_params['sort'] = filter_field

        LOGGER.info('{} - Syncing data since {} - limit: {}, offset: {}'.format(
            stream.tap_stream_id,
            last_datetime,
            count,
            offset))

        data = client.get(
            stream_config['url_path'],
            params=query_params,
            endpoint=stream_name)
        records = data['data']

        if len(records) < count:
            has_more = False
        else:
            offset += count

        max_modified = process_records(stream,
                                       mdata,
                                       max_modified,
                                       records,
                                       filter_field,
                                       fks)

        if offset > 10000:
            paginate_datetime = max_modified
            offset = 0

        if stream_config.get('replication') == 'incremental':
            write_bookmark(state, stream_name, max_modified)

def update_current_stream(state, stream_name=None):  
    set_currently_syncing(state, stream_name) 
    singer.write_state(state)

def sync(client, catalog, state, start_date):
    if not catalog:
        catalog = discover()
        selected_streams = catalog.streams
    else:
        selected_streams = catalog.get_selected_streams(state)

    selected_streams = sorted(selected_streams, key=lambda x: x.tap_stream_id)

    for stream in selected_streams:
        mdata = metadata.to_map(stream.metadata)
        update_current_stream(state, stream.tap_stream_id)
        sync_endpoint(client, catalog, state, start_date, stream, mdata)

    update_current_stream(state)

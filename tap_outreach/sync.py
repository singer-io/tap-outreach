import singer
from singer import metrics, metadata, Transformer
from singer.bookmarks import set_currently_syncing

LOGGER = singer.get_logger()

STREAM_CONFIGS = {
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
            'phoneNumberId',
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
        'fks': [
            'accountId',
            'callId',
            'mailingId',
            'opportunityId',
            'prospectId',
            'taskId',
            'userId'
        ]
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
            'followUpSequenceId',
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
            'ownerId',
            'stageId',
            'updaterId'
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
            'ownerId',
            'personaId',
            'stageId',
            'updaterId'
        ]
    },
    'sequence_states': {
        'url_path': 'sequenceStates',
        'replication': 'incremental',
        'filter_field': 'updatedAt',
        'fks': [
            'accountId',
            'creatorId',
            'mailboxId',
            'opportunityId',
            'prospectId',
            'sequenceId',
            'sequenceStepId'
        ]
    },
    'sequence_steps': {
        'url_path': 'sequenceSteps',
        'replication': 'incremental',
        'filter_field': 'updatedAt',
        'fks': [
            'callPurposeId',
            'creatorId',
            'sequenceId',
            'taskPriorityId',
            'updaterId'
        ]
    },
    'sequence_templates': {
        'url_path': 'sequenceTemplates',
        'replication': 'full',
        'fks': ['creatorId', 'sequenceStepId', 'templateId', 'updaterId']
    },
    'sequences': {
        'url_path': 'sequences',
        'replication': 'incremental',
        'filter_field': 'updatedAt',
        'fks': ['creatorId', 'ownerId', 'rulesetId', 'updaterId']
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
            'sequenceTemplateId',
            'subjectId',
            'taskPriorityId',
            'templateId'
        ]
    },
    'teams': {
        'url_path': 'teams',
        'replication': 'incremental',
        'filter_field': 'updatedAt',
        'fks': ['creatorId', 'updaterId']
    },
    'users': {
        'url_path': 'users',
        'replication': 'incremental',
        'filter_field': 'updatedAt',
        'fks': [
            'mailboxId',
            'profileId',
            'roleId',
            'creatorId',
            'updaterId'
        ]
    }
}


def get_bookmark(state, stream_name, default):
    return state.get('bookmarks', {}).get(stream_name, {}).get(STREAM_CONFIGS[stream_name].get('filter_field'), default)


def write_bookmark(state, stream_name, value):
    if 'bookmarks' not in state:
        state['bookmarks'] = {}
    state['bookmarks'][stream_name] = {STREAM_CONFIGS[stream_name]['filter_field']: value}
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
                    raise Exception(
                        'Error flattening Outeach record - conflict with `id` key')
                record_flat[prop] = value

            if 'relationships' in record:
                for prop, value in record['relationships'].items():
                    if 'data' not in value and 'links' not in value:
                        LOGGER.warning("Skipping invalid value: %s only when `data` and `links` not in relationships", prop)
                        continue
                    fk_field_name = '{}Id'.format(prop)

                    if 'data' in value and fk_field_name in fks:
                        data_value = value['data']
                        if data_value is not None and 'id' not in data_value:
                            raise Exception(
                                'null or `id` field expected for `data` relationship')

                        if data_value is not None:
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


def sync_endpoint(client, config, state, start_date, stream, mdata):
    stream_name = stream.tap_stream_id
    last_datetime = get_bookmark(state, stream_name, start_date)

    write_schema(stream)

    stream_config = STREAM_CONFIGS[stream_name]
    filter_field = stream_config.get('filter_field')
    fks = stream_config.get('fks', [])

    # Pagination: https://api.outreach.io/api/v2/docs#pagination
    # Changed to cursor-based pagination (not offset); offset still used for logging
    offset = 0
    count = int(config.get('page_size', 250))
    has_more = True
    max_modified = last_datetime
    paginate_datetime = last_datetime
    page = 1
    next_url = None

    while has_more:
        # query_params only needed for first page, next_url incl. params
        if page == 1:
            query_params = {
                'page[size]': count,
                'count': 'false'
            }
            if stream_config.get('replication') == 'incremental':
                query_params['filter[{}]'.format(
                    filter_field)] = '{}..inf'.format(paginate_datetime)
                query_params['sort'] = filter_field

        LOGGER.info(f"{stream.tap_stream_id} - Syncing data since {last_datetime} \
                    - page: {page}, limit: {count}, offset: {offset}")

        querystring = '&'.join(['%s=%s' % (key, value)
                                for (key, value) in query_params.items()])
        if page == 1:
            data = client.get(
                path=stream_config['url_path'],
                params=querystring,
                endpoint=stream_name)
        else:  # next_url
            data = client.get(
                url=next_url,
                params=query_params,
                endpoint=stream_name)

        records = data.get('data', [])
        next_url = data.get('links', {}).get('next', None)

        if not next_url:
            has_more = False
        else:
            # LOGGER.info('next_url: {}'.format(next_url))
            offset += count
            page = page + 1

        max_modified = process_records(stream,
                                       mdata,
                                       max_modified,
                                       records,
                                       filter_field,
                                       fks)

        if stream_config.get('replication') == 'incremental':
            write_bookmark(state, stream_name, max_modified)


def update_current_stream(state, stream_name=None):
    LOGGER.info("Setting the stream as currently syncing")
    set_currently_syncing(state, stream_name)
    singer.write_state(state)


def sync(client, config, catalog, state, start_date):
    selected_streams = catalog.get_selected_streams(state)

    for stream in selected_streams:
        mdata = metadata.to_map(stream.metadata)
        update_current_stream(state, stream.tap_stream_id)
        sync_endpoint(client, config, state,
                      start_date, stream, mdata)

    update_current_stream(state)

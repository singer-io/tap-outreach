import os
import json
import singer
from singer import metadata
from singer.catalog import Catalog, CatalogEntry, Schema
from .sync import STREAM_CONFIGS
from .client import OutreachForbiddenError

LOGGER = singer.get_logger()


def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def get_schemas():
    schemas = {}
    schemas_metadata = {}
    schemas_path = get_abs_path('schemas')

    file_names = sorted([f for f in os.listdir(schemas_path)
                  if os.path.isfile(os.path.join(schemas_path, f))])

    for file_name in file_names:
        stream_name = file_name[:-5]
        with open(os.path.join(schemas_path, file_name)) as data_file:
            schema = json.load(data_file)

        refs = schema.pop("definitions", {})
        if refs:
            singer.resolve_schema_references(schema, refs)

        replication = STREAM_CONFIGS[stream_name]['replication']
        replication_key = STREAM_CONFIGS[stream_name].get('filter_field', None)
        meta = metadata.get_standard_metadata(
            schema=schema,
            key_properties=['id'],
            valid_replication_keys=[replication_key] if replication_key else [],
            replication_method='FULL_TABLE' if replication == 'full' else replication.upper()
        )

        meta = metadata.to_map(meta)

        if replication == 'incremental':
            meta = metadata.write(
                meta, ('properties', STREAM_CONFIGS[stream_name]['filter_field']), 'inclusion', 'automatic')

        meta = metadata.to_list(meta)

        schemas[stream_name] = schema
        schemas_metadata[stream_name] = meta

    return schemas, schemas_metadata


def _check_stream_access(client, stream_name):
    """
    Make a minimal probe request to verify read access to a stream.
    Returns True if accessible, False if a 403 Forbidden error is raised.
    """
    url_path = STREAM_CONFIGS[stream_name]['url_path']
    try:
        client.get(path=url_path, params='page[size]=1&count=false', endpoint=stream_name)
        return True
    except OutreachForbiddenError:
        LOGGER.warning(
            "Stream '%s' does not have read permission (403), excluding from catalog.",
            stream_name,
        )
        return False


def _prune_inaccessible_children(schemas: dict, field_metadata: dict) -> None:
    """
    Remove child streams from the catalog whose parent stream was excluded.
    Mutates schemas and field_metadata in place.
    Note: tap-outreach has no parent-child stream relationships, so this is a no-op.
    Included for pattern consistency with other Singer taps.
    """


def _apply_access_checks(client, schemas: dict, field_metadata: dict) -> None:
    """
    Probe each stream for read access and remove inaccessible streams from
    schemas and field_metadata in place.
    Raises OutreachForbiddenError if no streams are accessible.
    """
    inaccessible_streams = [
        stream_name
        for stream_name in list(schemas.keys())
        if not _check_stream_access(client, stream_name)
    ]

    for stream_name in inaccessible_streams:
        schemas.pop(stream_name, None)
        field_metadata.pop(stream_name, None)

    _prune_inaccessible_children(schemas, field_metadata)

    if inaccessible_streams:
        if not schemas:
            raise OutreachForbiddenError(
                "HTTP-error-code: 403, Error: The account credentials supplied do not have 'read' access to any "
                "of the streams supported by the tap. Data collection cannot be initiated due to lack of permissions."
            )
        LOGGER.warning(
            "The account credentials supplied do not have 'read' access to the following stream(s): %s. "
            "These streams have been excluded from the catalog.",
            ", ".join(inaccessible_streams),
        )


def discover(client) -> Catalog:
    """
    Run the discovery mode, prepare the catalog file and return the catalog.
    Access to each stream is verified using the provided client and streams
    the credentials cannot read are excluded from the returned catalog.
    """
    schemas, field_metadata = get_schemas()
    _apply_access_checks(client, schemas, field_metadata)

    catalog = Catalog([])

    for stream_name, schema_dict in schemas.items():
        schema = Schema.from_dict(schema_dict)
        mdata = field_metadata[stream_name]

        catalog.streams.append(CatalogEntry(
            stream=stream_name,
            tap_stream_id=stream_name,
            key_properties=['id'],
            schema=schema,
            metadata=mdata
        ))

    return catalog

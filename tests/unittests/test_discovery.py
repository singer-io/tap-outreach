import unittest
from unittest.mock import MagicMock, patch

from tap_outreach.client import OutreachForbiddenError
from tap_outreach.discover import (
    _apply_access_checks,
    _check_stream_access,
    discover,
    get_schemas,
)
from tap_outreach.sync import STREAM_CONFIGS


class TestGetSchemas(unittest.TestCase):
    """Verify that get_schemas() loads schemas for all expected streams."""

    def test_all_streams_have_schemas(self):
        schemas, field_metadata = get_schemas()
        self.assertEqual(set(schemas.keys()), set(STREAM_CONFIGS.keys()))
        self.assertEqual(set(field_metadata.keys()), set(STREAM_CONFIGS.keys()))

    def test_schema_is_dict(self):
        schemas, _ = get_schemas()
        for stream_name, schema in schemas.items():
            self.assertIsInstance(schema, dict, f"Schema for '{stream_name}' should be a dict")

    def test_metadata_is_list(self):
        _, field_metadata = get_schemas()
        for stream_name, meta in field_metadata.items():
            self.assertIsInstance(meta, list, f"Metadata for '{stream_name}' should be a list")

    def test_incremental_streams_have_replication_key_in_metadata(self):
        schemas, field_metadata = get_schemas()
        for stream_name, config in STREAM_CONFIGS.items():
            if config['replication'] == 'incremental':
                meta_entries = field_metadata[stream_name]
                automatic_fields = [
                    e['metadata'].get('inclusion')
                    for e in meta_entries
                    if e.get('breadcrumb') == ('properties', config['filter_field'])
                ]
                self.assertIn(
                    'automatic', automatic_fields,
                    f"Stream '{stream_name}' filter_field should have inclusion=automatic"
                )

    def test_full_table_streams_have_correct_replication_method(self):
        _, field_metadata = get_schemas()
        for stream_name, config in STREAM_CONFIGS.items():
            if config['replication'] == 'full':
                root_meta = next(
                    (e['metadata'] for e in field_metadata[stream_name] if e.get('breadcrumb') == ()),
                    {}
                )
                self.assertEqual(
                    root_meta.get('forced-replication-method'), 'FULL_TABLE',
                    f"Stream '{stream_name}' should have FULL_TABLE replication"
                )


class TestCheckStreamAccess(unittest.TestCase):
    """Unit tests for _check_stream_access()."""

    def setUp(self):
        self.client = MagicMock()
        self.stream_name = 'accounts'

    def test_returns_true_when_accessible(self):
        self.client.get.return_value = {'data': []}
        result = _check_stream_access(self.client, self.stream_name)
        self.assertTrue(result)

    def test_returns_false_on_forbidden(self):
        self.client.get.side_effect = OutreachForbiddenError('403 Forbidden')
        result = _check_stream_access(self.client, self.stream_name)
        self.assertFalse(result)

    def test_probe_uses_correct_url_path(self):
        self.client.get.return_value = {'data': []}
        _check_stream_access(self.client, self.stream_name)
        self.client.get.assert_called_once_with(
            path=STREAM_CONFIGS[self.stream_name]['url_path'],
            params='page[size]=1&count=false',
            endpoint=self.stream_name,
        )

    def test_non_403_exception_propagates(self):
        self.client.get.side_effect = Exception('Network error')
        with self.assertRaises(Exception):
            _check_stream_access(self.client, self.stream_name)


class TestApplyAccessChecks(unittest.TestCase):
    """Unit tests for _apply_access_checks()."""

    def setUp(self):
        self.client = MagicMock()
        self.schemas = {'accounts': {'type': 'object'}, 'calls': {'type': 'object'}}
        self.field_metadata = {'accounts': [], 'calls': []}

    @patch('tap_outreach.discover._check_stream_access', return_value=True)
    def test_all_accessible_leaves_dicts_unchanged(self, mock_check):
        _apply_access_checks(self.client, self.schemas, self.field_metadata)
        self.assertIn('accounts', self.schemas)
        self.assertIn('calls', self.schemas)

    @patch('tap_outreach.discover._check_stream_access')
    def test_inaccessible_stream_is_removed(self, mock_check):
        mock_check.side_effect = lambda client, name: name != 'calls'
        _apply_access_checks(self.client, self.schemas, self.field_metadata)
        self.assertIn('accounts', self.schemas)
        self.assertNotIn('calls', self.schemas)
        self.assertNotIn('calls', self.field_metadata)

    @patch('tap_outreach.discover._check_stream_access', return_value=False)
    def test_all_inaccessible_raises_forbidden_error(self, mock_check):
        with self.assertRaises(OutreachForbiddenError):
            _apply_access_checks(self.client, self.schemas, self.field_metadata)

    @patch('tap_outreach.discover._check_stream_access')
    def test_partial_inaccessible_logs_warning(self, mock_check):
        mock_check.side_effect = lambda client, name: name != 'calls'
        with patch('tap_outreach.discover.LOGGER') as mock_logger:
            _apply_access_checks(self.client, self.schemas, self.field_metadata)
            mock_logger.warning.assert_called_once()
            warning_msg = mock_logger.warning.call_args[0][0]
            self.assertIn("No 'read' access", warning_msg)

    @patch('tap_outreach.discover._check_stream_access', return_value=True)
    def test_all_accessible_no_warning_logged(self, mock_check):
        with patch('tap_outreach.discover.LOGGER') as mock_logger:
            _apply_access_checks(self.client, self.schemas, self.field_metadata)
            mock_logger.warning.assert_not_called()

    @patch('tap_outreach.discover._check_stream_access', return_value=False)
    def test_all_inaccessible_error_message(self, mock_check):
        with self.assertRaises(OutreachForbiddenError) as ctx:
            _apply_access_checks(self.client, self.schemas, self.field_metadata)
        self.assertIn('403', str(ctx.exception))
        self.assertIn("do not have 'read' access to any supported streams", str(ctx.exception))

    @patch('tap_outreach.discover._check_stream_access', return_value=False)
    def test_all_inaccessible_exact_error_message(self, mock_check):
        """Validate the exact error message raised when no streams are accessible."""
        expected_message = (
            "HTTP-error-code: 403, Error: The credentials "
            "do not have 'read' access to any supported streams."
        )
        with self.assertRaises(OutreachForbiddenError) as ctx:
            _apply_access_checks(self.client, self.schemas, self.field_metadata)
        self.assertEqual(expected_message, str(ctx.exception))


class TestDiscover(unittest.TestCase):
    """Unit tests for discover()."""

    def setUp(self):
        self.client = MagicMock()

    @patch('tap_outreach.discover._apply_access_checks')
    def test_discover_returns_catalog(self, mock_access):
        from singer.catalog import Catalog
        catalog = discover(self.client)
        self.assertIsInstance(catalog, Catalog)

    @patch('tap_outreach.discover._apply_access_checks')
    def test_discover_catalog_contains_all_streams(self, mock_access):
        catalog = discover(self.client)
        stream_ids = {s.tap_stream_id for s in catalog.streams}
        self.assertEqual(stream_ids, set(STREAM_CONFIGS.keys()))

    @patch('tap_outreach.discover._apply_access_checks')
    def test_discover_streams_have_key_properties(self, mock_access):
        catalog = discover(self.client)
        for stream in catalog.streams:
            self.assertEqual(stream.key_properties, ['id'])

    @patch('tap_outreach.discover._apply_access_checks')
    def test_discover_passes_client_to_access_checks(self, mock_access):
        discover(self.client)
        mock_access.assert_called_once()
        args = mock_access.call_args[0]
        self.assertIs(args[0], self.client)

    @patch('tap_outreach.discover._apply_access_checks')
    def test_discover_excludes_stream_removed_by_access_check(self, mock_access):
        def remove_calls(client, schemas, field_metadata):
            schemas.pop('calls', None)
            field_metadata.pop('calls', None)

        mock_access.side_effect = remove_calls
        catalog = discover(self.client)
        stream_ids = {s.tap_stream_id for s in catalog.streams}
        self.assertNotIn('calls', stream_ids)

    def test_discover_raises_when_all_streams_forbidden(self):
        with patch('tap_outreach.discover._check_stream_access', return_value=False):
            with self.assertRaises(OutreachForbiddenError):
                discover(self.client)

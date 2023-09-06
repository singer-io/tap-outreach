import unittest
from tap_outreach.sync import process_records


class MockSchema:
    def to_dict(self):
        pass


class MockStream:
    def __init__(self) -> None:
        self.tap_stream_id = "mock_stream"
        self.schema = MockSchema()


class TestProcessRecord(unittest.TestCase):
    """A set of unit tests to ensure that the process_record raise the exception
    on any discrepancy within the response data"""

    def test_conflict_id(self):
        """call `process_records` function and by passing the `mock_id_records` in
        the param.
        We expect the exception to be raised -
        `Error flattening Outeach record - conflict with `id` key`
        """
        mock_records = [{"id": 1, "attributes": {"id": 2}}]
        mock_stream = MockStream()
        with self.assertRaises(Exception) as e:
            process_records(
                mock_stream,
                "mock_mdata",
                "mock_max_modified",
                mock_records,
                "mock_filter_field",
                "mock_fks",
            )
        self.assertEqual(e.exception.args[0], 'Error flattening Outeach record - conflict with `id` key')

    def test_conflict_data_links(self):
        """call `process_records` function and by passing the `mock_id_records` in
        the param.
        We expect the exception to be raised -
        `Only `data` or `links` expected in relationships`
        """
        mock_records = [{"id": 1, "attributes": {}, "relationships": {"prop": {"value": ""}}}]
        mock_stream = MockStream()
        with self.assertRaises(Exception) as e:
            process_records(
                mock_stream,
                "mock_mdata",
                "mock_max_modified",
                mock_records,
                "mock_filter_field",
                "mock_fks",
            )
        self.assertEqual(e.exception.args[0], 'Only `data` or `links` expected in relationships')

    def test_conflict_data_id(self):
        """call `process_records` function and by passing the `mock_id_records` in
        the param.
        We expect the exception to be raised -
        `null or `id` field expected for `data` relationship`
        """
        mock_records = [{"id": 1, "attributes": {}, "relationships": {"prop": {"data": "data_value"}}}]
        mock_stream = MockStream()
        mock_fks = ["propId"]
        with self.assertRaises(Exception) as e:
            process_records(
                mock_stream,
                "mock_mdata",
                "mock_max_modified",
                mock_records,
                "mock_filter_field",
                mock_fks
            )
        self.assertEqual(e.exception.args[0], 'null or `id` field expected for `data` relationship')

    def test_conflict_prospects_attributes(self):
        """call `process_records` function and by passing the `mock_id_records` in
        the param.
        We expect the exception to be raised -
        ``propId` exists as both an attribute and generated relationship name`
        """
        mock_records = [{"id": 1, "attributes": {"propId": 456}, "relationships": {"prop": {"data": {"id": 123}}}}]
        mock_stream = MockStream()
        mock_fks = ["propId"]
        with self.assertRaises(Exception) as e:
            process_records(
                mock_stream,
                "mock_mdata",
                "mock_max_modified",
                mock_records,
                "mock_filter_field",
                mock_fks
            )
        self.assertEqual(e.exception.args[0], '`propId` exists as both an attribute and generated relationship name')

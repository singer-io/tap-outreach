from tap_tester import connections, runner
from tap_tester.base_suite_tests.pagination_test import PaginationTest
from base import OutreachBase


class OutreachPaginationTest(PaginationTest, OutreachBase):
    """Standard Pagination Test"""

    @staticmethod
    def name():
        return "tt_outreach_pagination_test"

    def expected_page_size(self, stream):
        return 1

    def streams_to_test(self):
        streams_to_exclude = {"mailings", "calls"}
        return self.expected_stream_names().difference(streams_to_exclude)

    def test_pagination_with_page_size_one(self):
        """Sync multiple one-record pages without duplicate primary keys."""
        def set_page_size(existing_connections, payload):
            payload["properties"]["page_size"] = "1"
            return payload

        conn_id = connections.ensure_connection(self, payload_hook=set_page_size)
        found_catalogs = self.run_and_verify_check_mode(conn_id)
        test_catalogs = [
            catalog for catalog in found_catalogs
            if catalog.get("stream_name") in self.streams_to_test()
        ]
        self.perform_and_verify_table_and_field_selection(conn_id, test_catalogs)

        record_counts = self.run_and_verify_sync_mode(conn_id)
        synced_records = runner.get_records_from_target_output()

        for stream in self.streams_to_test():
            with self.subTest(stream=stream):
                record_count = record_counts.get(stream, -1)
                self.assertGreater(record_count, 1)
                primary_keys = self.expected_primary_keys(stream)
                unique_keys = {
                    tuple(message["data"][key] for key in primary_keys)
                    for message in synced_records.get(stream, {}).get("messages", [])
                    if message.get("action") == "upsert"
                }
                self.assertEqual(len(unique_keys), record_count)

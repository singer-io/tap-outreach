from datetime import datetime

from tap_tester.base_suite_tests.bookmark_test import BookmarkTest
from base import OutreachBase

# from debugpy import listen, wait_for_client
# listen(8000)
# wait_for_client()

class OutreachBookmarkTest(BookmarkTest, OutreachBase):
    """Standard Bookmark Test"""

    bookmark_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    initial_bookmarks = {
        "bookmarks": {
            "accounts": {"updatedAt": "2016-07-07T14:22:04.624Z"},
            "call_dispositions": {"updatedAt": "2020-05-06T18:54:08.250Z"},
            "call_purposes": {"updatedAt": "2020-11-06T20:17:17Z"},
            "calls": {"updatedAt": "2018-01-17T13:45:25.125Z"},
            "content_categories": {"updatedAt": "2019-10-10T03:23:15.466Z"},
            "events": {"updatedAt": "2016-07-07T14:22:04.624Z"},
            "mailboxes": {"updatedAt": "2020-05-06T18:54:08.250Z"},
            # "mailings": {"updatedAt": "2020-11-06T20:17:17Z"},
            "opportunities": {"updatedAt": "2018-01-17T13:45:25.125Z"},
            "personas": {"updatedAt": "2019-10-10T03:23:15.466Z"},
            "prospects": {"updatedAt": "2016-07-07T14:22:04.624Z"},
            "stages": {"updatedAt": "2020-05-06T18:54:08.250Z"},
            "sequences": {"updatedAt": "2020-11-06T20:17:17Z"},
            "sequence_steps": {"updatedAt": "2019-10-10T03:23:15.466Z"},
            "tasks": {"updatedAt": "2020-05-06T18:54:08.250Z"},
            "users": {"updatedAt": "2019-10-10T03:23:15.466Z"},
        }
    }

    @property
    def start_date(self):
        return "2015-03-25T00:00:00Z"

    @staticmethod
    def name():
        return "tt_outreach_bookmark_test"

    def streams_to_test(self):
        # Skip streams due to lack of test data
        streams_to_exclude = {"mailings", "duties", "sequence_templates", "teams", "sequence_states"}
        return self.expected_stream_names().difference(streams_to_exclude)

    def test_bookmark_format(self):
        """Outreach bookmarks use UTC timestamps with optional fractional seconds."""
        for stream in self.test_streams:
            for sync_number, bookmarks in enumerate(
                    (self.bookmark_values_1, self.bookmark_values_2), start=1):
                with self.subTest(stream=stream, sync=sync_number):
                    replication_method = self.expected_replication_methods.get(stream, {})
                    value = bookmarks.get(stream, {})
                    if replication_method == self.INCREMENTAL:
                        self.assertIsNotNone(value)
                        self.assertIsInstance(value, str)
                        self.assertRegex(
                            value,
                            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z\Z",
                        )
                        timestamp_format = (
                            self.bookmark_format if "." in value else "%Y-%m-%dT%H:%M:%SZ"
                        )
                        self.assertIsInstance(datetime.strptime(value, timestamp_format), datetime)
                    elif replication_method == self.FULL_TABLE:
                        self.assertIsNone(value)

    def calculate_new_bookmarks(self):
        """
        Calculates new bookmarks by looking through sync 1 data to determine a bookmark
        that will sync 2 records in sync 2 (plus any necessary look back data)
        """
        new_bookmarks = super().calculate_new_bookmarks()
        return {key: {k: v.replace(".000000Z", ".000Z") for k, v in value.items()}
                for key, value in new_bookmarks.items()}

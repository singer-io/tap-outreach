from tap_tester.base_suite_tests.bookmark_test import BookmarkTest
from base import OutreachBase


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
            "sequence_states": {"updatedAt": "2018-01-17T13:45:25.125Z"},
            "sequence_steps": {"updatedAt": "2019-10-10T03:23:15.466Z"},
            "tasks": {"updatedAt": "2020-05-06T18:54:08.250Z"},
            "teams": {"updatedAt": "2020-11-06T20:17:17Z"},
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
        streams_to_exclude = {"mailings", "duties", "sequence_templates"}
        return self.expected_stream_names().difference(streams_to_exclude)

    def calculate_new_bookmarks(self):
        """
        Calculates new bookmarks by looking through sync 1 data to determine a bookmark
        that will sync 2 records in sync 2 (plus any necessary look back data)
        """
        new_bookmarks = {}
        for stream, records in self.synced_records_1.items():
            replication_method = self.expected_replication_method(stream)
            if replication_method == self.INCREMENTAL:
                look_back = self.expected_lookback_window(stream)
                replication_key = self.expected_replication_keys(stream)
                assert len(replication_key) == 1
                replication_key = next(iter(replication_key))

                # get the replication values that are prior to the lookback window
                replication_values = sorted({
                    message['data'][replication_key] for message in records['messages']
                    if message['action'] == 'upsert'
                    and self.parse_date(message['data'][replication_key]) <
                    self.parse_date(self.get_bookmark_value(
                        self.state_1, self.get_stream_id(stream))) - look_back})
                print(
                    f"unique replication values for stream {stream} are: {replication_values}")

                # There should be 3 or more records (prior to the look back window)
                # so we can set the bookmark to get the last 2 records (+ the look back)
                # self.assertGreater(len(replication_values), 2,
                #                    msg="We need to have more than two replication dates "
                #                        "to test a stream")
                try:
                    # Tap expects date format "%Y-%m-%dT%H:%M:%S.000Z" which is not handled by
                    # base test suite so handling it in the test class explicitl
                    new_bookmarks[self.get_stream_id(stream)] = {
                        replication_key:
                        self.timedelta_formatted(self.parse_date(replication_values[-2]),
                                                 date_format=self.bookmark_format).replace(".000000Z", ".000Z")}
                except IndexError as e:
                    raise Exception(f"{stream}: {replication_values}") from e
        return new_bookmarks

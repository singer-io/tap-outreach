from tap_tester.base_suite_tests.bookmark_test import BookmarkTest
from base import OutreachBase


class OutreachAllFieldsTest(BookmarkTest, OutreachBase):
    """Standard Bookmark Test"""

    bookmark_format = "%Y-%m-%dT%H:%M:%S.Z"
    initial_bookmarks = {
        "bookmarks": {
            "accounts": {"updatedAt": "2016-07-07T14:22:04.624Z"},
            "call_dispositions": {"updatedAt": "2020-05-06T18:54:08.250Z"},
            "call_purposes": {"updatedAt": "2020-11-06T20:17:17Z"},
            "calls": {"updatedAt": "2018-01-17T13:45:25.125Z"},
            "content_categories": {"updatedAt": "2019-10-10T03:23:15.466Z"},
            "events": {"updatedAt": "2016-07-07T14:22:04.624Z"},
            "mailboxes": {"updatedAt": "2020-05-06T18:54:08.250Z"},
            "mailings": {"updatedAt": "2020-11-06T20:17:17Z"},
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

    @staticmethod
    def name():
        return "tt_outreach_bookmark_test"

    def streams_to_test(self):
        streams_to_exclude = {"mailings", "duties"}
        return self.expected_stream_names().difference(streams_to_exclude)

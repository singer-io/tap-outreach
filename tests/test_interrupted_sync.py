from tap_tester.base_suite_tests.interrupted_sync_test import InterruptedSyncTest
from base import OutreachBase


class OutreachInterruptedSyncTest(InterruptedSyncTest, OutreachBase):
    """Standard Interrupted Sync Test"""

    @staticmethod
    def name():
        return "tt_outreach_interrupted_sync_test"

    def streams_to_test(self):
        streams_to_exclude = {"mailings", "duties", "sequence_templates"}
        return self.expected_stream_names().difference(streams_to_exclude)

    def manipulate_state(self):
        return {
            "currently_syncing": "prospects",
            "bookmarks": {
                "mailboxes": {"updatedAt": "2023-08-31T17:49:56.Z"},
                "calls": {"updatedAt": "2023-09-13T21:07:04.Z"},
                "prospects": {"updatedAt": "2023-07-31T18:23:54.Z"},
                "call_dispositions": {"updatedAt": "2023-09-13T20:38:36.Z"},
                "call_purposes": {"updatedAt": "2023-09-13T20:50:34.Z"},
                "content_categories": {"updatedAt": "2023-08-31T14:59:57.Z"},
                "personas": {"updatedAt": "2023-08-31T18:00:58.Z"},
                "opportunities": {"updatedAt": "2023-08-31T14:52:57.Z"},
                "accounts": {"updatedAt": "2023-09-13T20:48:48.Z"},
                "events": {"eventAt": "2023-09-13T21:07:04.Z"},
            },
        }

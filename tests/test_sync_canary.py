from tap_tester.base_suite_tests.sync_canary_test import SyncCanaryTest
from base import OutreachBase


class OutreachSyncCanaryTest(SyncCanaryTest, OutreachBase):
    """Standard Sync Canary Test"""

    @staticmethod
    def name():
        return "tt_outreach_sync_canary_test"

    def streams_to_test(self):
        streams_to_exclude = {"mailings"}
        return self.expected_stream_names().difference(streams_to_exclude)

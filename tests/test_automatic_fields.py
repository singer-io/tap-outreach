from tap_tester.base_suite_tests.automatic_fields_test import MinimumSelectionTest
from base import OutreachBase


class OutreachMinimumSelectionTest(MinimumSelectionTest, OutreachBase):
    """Standard Automatic Fields Test"""

    @staticmethod
    def name():
        return "tt_outreach_auto"

    def streams_to_test(self):
        streams_to_exclude = {
            "mailings",
            "duties",
            "users",
            "sequence_states",
            "sequences",
        }
        return self.expected_stream_names().difference(streams_to_exclude)

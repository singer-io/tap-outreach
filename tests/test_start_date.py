from tap_tester.base_suite_tests.start_date_test import StartDateTest
from base import OutreachBase



class OutreachStartdateTest(StartDateTest, OutreachBase):
    """Standard Start date Test"""

    bookmark_format = "%Y-%m-%dT%H:%M:%S.%fZ"

    @staticmethod
    def name():
        return "tt_outreach_start_date_test"

    def streams_to_test(self):
        # Skip streams due to lack of test data
        streams_to_exclude = {"mailings", "prospects", "sequence_states", "duties", "sequence_templates"}
        return self.expected_stream_names().difference(streams_to_exclude)

    @property
    def start_date_1(self):
        return "2015-03-25T00:00:00Z"

    @property
    def start_date_2(self):
        return "2023-09-01T00:00:00Z"

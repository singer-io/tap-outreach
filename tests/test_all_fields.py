from tap_tester.base_suite_tests.all_fields_test import AllFieldsTest
from base import OutreachBase


class OutreachAllFieldsTest(AllFieldsTest, OutreachBase):
    """Standard All Fields Test"""
    MISSING_FIELDS = {
        "sequence_templates": {"negaitveReplyCount"},
        "tasks": {"taskThemeId"},
    }

    @staticmethod
    def name():
        return "tt_outreach_all_fields_test"

    def streams_to_test(self):
        streams_to_exclude = {"mailings"}
        return self.expected_stream_names().difference(streams_to_exclude)

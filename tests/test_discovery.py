from tap_tester.base_suite_tests.discovery_test import DiscoveryTest
from base import OutreachBase


class OutreachDiscoveryTest(DiscoveryTest, OutreachBase):
    """Standard Discovery Test"""

    @staticmethod
    def name():
        return "tt_outreach_discovery"

    def streams_to_test(self):
        return self.expected_stream_names()

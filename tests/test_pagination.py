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

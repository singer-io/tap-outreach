import os

from tap_tester.base_suite_tests.base_case import BaseCase


class OutreachBase(BaseCase):
    """
    Setup expectations for test sub classes.
    Metadata describing streams.
    A bunch of shared methods that are used in tap-tester tests.
    Shared tap-specific methods (as needed).
    """
    PAGE_SIZE = 100000
    start_date = "2019-01-01T00:00:00Z"

    @staticmethod
    def tap_name():
        """The name of the tap"""
        return "tap-outreach"

    @staticmethod
    def get_type():
        """the expected url route ending"""
        return "platform.outreach"

    def get_properties(self, original: bool = True):
        """Configuration properties required for the tap."""

        return_value = {
            "start_date": self.start_date,
            "redirect_uri": "https://app.stitchdata.test:8080/v2/integrations/platform.outreach/callback",
            "client_id": os.getenv("TAP_OUTREACH_CLIENT_ID"),
            "client_secret": os.getenv("TAP_OUTREACH_CLIENT_SECRET"),
            "refresh_token": os.getenv("TAP_OUTREACH_REFRESH_TOKEN"),
        }

        return return_value

    @staticmethod
    def get_credentials():
        return {
            "client_id": os.getenv("TAP_OUTREACH_CLIENT_ID"),
            "client_secret": os.getenv("TAP_OUTREACH_CLIENT_SECRET"),
            "refresh_token": os.getenv("TAP_OUTREACH_REFRESH_TOKEN"),
        }

    @classmethod
    def expected_metadata(self):
        """The expected streams and metadata about the streams"""

        return {
            "accounts": {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_KEYS: {"updatedAt"},
                self.REPLICATION_METHOD: self.INCREMENTAL,
            },
            "call_dispositions": {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_KEYS: {"updatedAt"},
                self.REPLICATION_METHOD: self.INCREMENTAL,
            },
            "call_purposes": {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_KEYS: {"updatedAt"},
                self.REPLICATION_METHOD: self.INCREMENTAL,
            },
            "calls": {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_KEYS: {"updatedAt"},
                self.REPLICATION_METHOD: self.INCREMENTAL,
            },
            "content_categories": {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_KEYS: {"updatedAt"},
                self.REPLICATION_METHOD: self.INCREMENTAL,
            },
            "duties": {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
            },
            "events": {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_KEYS: {"eventAt"},
                self.REPLICATION_METHOD: self.INCREMENTAL,
            },
            "mailboxes": {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_KEYS: {"updatedAt"},
                self.REPLICATION_METHOD: self.INCREMENTAL,
            },
            "mailings": {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_KEYS: {"updatedAt"},
                self.REPLICATION_METHOD: self.INCREMENTAL,
            },
            "opportunities": {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_KEYS: {"updatedAt"},
                self.REPLICATION_METHOD: self.INCREMENTAL,
            },
            "personas": {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_KEYS: {"updatedAt"},
                self.REPLICATION_METHOD: self.INCREMENTAL,
            },
            "prospects": {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_KEYS: {"updatedAt"},
                self.REPLICATION_METHOD: self.INCREMENTAL,
            },
            "stages": {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_KEYS: {"updatedAt"},
                self.REPLICATION_METHOD: self.INCREMENTAL,
            },
            "sequences": {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_KEYS: {"updatedAt"},
                self.REPLICATION_METHOD: self.INCREMENTAL,
            },
            "sequence_states": {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_KEYS: {"updatedAt"},
                self.REPLICATION_METHOD: self.INCREMENTAL,
            },
            "sequence_steps": {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_KEYS: {"updatedAt"},
                self.REPLICATION_METHOD: self.INCREMENTAL,
            },
            "sequence_templates": {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_METHOD: self.FULL_TABLE,
            },
            "tasks": {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_KEYS: {"updatedAt"},
                self.REPLICATION_METHOD: self.INCREMENTAL,
            },
            "teams": {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_KEYS: {"updatedAt"},
                self.REPLICATION_METHOD: self.INCREMENTAL,
            },
            "users": {
                self.PRIMARY_KEYS: {"id"},
                self.REPLICATION_KEYS: {"updatedAt"},
                self.REPLICATION_METHOD: self.INCREMENTAL,
            },
        }

    @classmethod
    def setUpClass(cls):
        super().setUpClass(logging="Ensuring environment variables are sourced.")
        missing_envs = [
            x
            for x in [
                "TAP_OUTREACH_CLIENT_ID",
                "TAP_OUTREACH_CLIENT_SECRET",
                "TAP_OUTREACH_REFRESH_TOKEN",
            ]
            if os.getenv(x) is None
        ]

        if len(missing_envs) != 0:
            raise Exception("Missing environment variables: {}".format(missing_envs))

    ##########################################################################
    ### Tap Specific Methods
    ##########################################################################

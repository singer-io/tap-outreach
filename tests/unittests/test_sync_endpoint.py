import unittest
from unittest.mock import patch
from tap_outreach import sync


class MockStream:
    def __init__(self) -> None:
        self.tap_stream_id = "accounts"


class MockClient:
    def get(self, path, params, endpoint):
        return {"data": "mock_data", "links": {}}


class SyncEndpoint(unittest.TestCase):
    """A set of unit tests to ensure the `sync_endpoint` functionality flow"""

    @patch("tap_outreach.sync.write_schema")
    @patch("tap_outreach.sync.process_records")
    def test_sync_endpoint(self, mock_process_record, mock_schema):
        """call `sync_endpoint` function and by passing the mock params.
        We expect the `process_records` to be called with below params.
        """

        mock_client = MockClient()
        mock_stream = MockStream()
        mock_config = {
            "start_date": "2023-01-01T00:00:00Z",
            "client_id": "mock_client",
            "client_secret": "mock_secret",
            "redirect_uri": "mock_uri",
            "refresh_token": "mock_token",
            "request_timeout": 5,
        }
        mock_state = {
            "currently_syncing": None,
            "bookmarks": {
                "accounts": "2023-07-07T05:30:59.000Z",
            },
        }

        sync.sync_endpoint(
            mock_client,
            mock_config,
            "mock_catalog",
            mock_state,
            mock_config["start_date"],
            mock_stream,
            "mock_mdata",
        )
        mock_process_record.assert_called_with(
            mock_stream,
            "mock_mdata",
            "2023-07-07T05:30:59.000Z",
            "mock_data",
            "updatedAt",
            ["creatorId", "ownerId", "updaterId"],
        )

import unittest
from unittest.mock import patch
import time
from requests.models import Response
from tap_outreach import client


class Mockresponse(Response):
    def __init__(self, status_code):
        super().__init__()
        self.status_code = status_code
        self.headers = {"x-ratelimit-reset": time.time()}

    def raise_for_status(self):
        pass


class TestRetryLogic(unittest.TestCase):
    """A set of unit tests to ensure that the retry logic work as expected"""

    @patch("tap_outreach.client.OutreachClient.refresh")
    @patch("tap_outreach.client.requests.Session.request")
    def test_retries_on_5XX(self, mock_session_request, _):
        """`OutreachClient.get()` calls a `request` method,to make a request to the API.
        We set the mock response status code to `500`.

        We expect the tap to retry this request up to 5 times, which is
        the current hard coded `max_tries` value.
        """

        # Create the mock and force the function to throw an error
        mock_session_request.return_value = Mockresponse(status_code=500)
        mocked_config = {
            "start_date": "2019-01-01T00:00:00Z",
            "client_id": "mock_client",
            "client_secret": "mock_secret",
            "redirect_uri": "mock_uri",
            "refresh_token": "mock_token",
            "request_timeout": 5,
        }

        # Initialize the object and call `get()`
        outreach_object = client.OutreachClient(mocked_config)
        with self.assertRaises(client.Server5xxError):
            outreach_object.get("mock_url", "mock_path")
        # 5 is the max tries specified in the tap
        self.assertEquals(5, mock_session_request.call_count)

    @patch("tap_outreach.client.OutreachClient.refresh")
    @patch("tap_outreach.client.OutreachClient.sleep_for_reset_period")
    @patch("tap_outreach.client.requests.Session.request")
    def test_retries_on_429(self, mock_session_request, *args):
        """`OutreachClient.get()` calls a `request` method,to make a request to the API.
        We set the mock response status code to `429`. Checks the execution on reaching
        rate limit.

        We expect the tap to retry this request up to 5 times, which is
        the current hard coded `max_tries` value.
        """

        # Create the mock and force the function to throw an error
        mock_session_request.return_value = Mockresponse(status_code=429)
        mocked_config = {
            "start_date": "2019-01-01T00:00:00Z",
            "client_id": "mock_client",
            "client_secret": "mock_secret",
            "redirect_uri": "mock_uri",
            "refresh_token": "mock_token",
            "request_timeout": 5,
        }

        # Initialize the object and call `get()`
        outreach_object = client.OutreachClient(mocked_config)
        with self.assertRaises(client.RateLimitError):
            outreach_object.get("mock_url", "mock_path")
        # 5 is the max tries specified in the tap
        self.assertEquals(5, mock_session_request.call_count)

    @patch("tap_outreach.client.OutreachClient.refresh")
    @patch("tap_outreach.client.OutreachClient.sleep_for_reset_period")
    @patch("tap_outreach.client.requests.Session.request")
    def test_retries_on_404(self, mock_session_request, *args):
        """`OutreachClient.get()` calls a `request` method,to make a request to the API.
        We set the mock response status code to `404`. Checks the execution on reaching
        rate limit.

        We expect the tap to retry this request up to 1 times, which is
        the current hard coded `max_tries` value.
        """

        # Create the mock and force the function to throw an error
        mock_session_request.return_value = Mockresponse(status_code=404)
        mocked_config = {
            "start_date": "2019-01-01T00:00:00Z",
            "client_id": "mock_client",
            "client_secret": "mock_secret",
            "redirect_uri": "mock_uri",
            "refresh_token": "mock_token",
            "request_timeout": 5,
        }

        # Initialize the object and call `get()`
        outreach_object = client.OutreachClient(mocked_config)
        with self.assertRaises(Exception):
            outreach_object.get("mock_url", "mock_path")
        # 5 is the max tries specified in the tap
        self.assertEquals(1, mock_session_request.call_count)

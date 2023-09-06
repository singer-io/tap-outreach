import unittest
from unittest import mock
from tap_outreach.client import OutreachClient, REQUEST_TIMEOUT
import requests
from parameterized import parameterized

class Mockresponse:
    """ Mock response object class."""

    def __init__(self, status_code, json, raise_error, headers={'X-RateLimit-Remaining': 1}, text=None, content=None):
        self.status_code = status_code
        self.raise_error = raise_error
        self.text = json
        self.headers = headers
        self.content = content if content is not None else 'github'

    def raise_for_status(self):
        if not self.raise_error:
            return self.status_code

        raise requests.HTTPError("Sample message")

    def json(self):
        """ Response JSON method."""
        return self.text

def get_response(status_code, json={}, raise_error=False, content=None):
    """ Returns required mock response. """
    return Mockresponse(status_code, json, raise_error, content=content)

@mock.patch("tap_outreach.client.requests.Session.request")
class TestTimeoutValue(unittest.TestCase):
    """
        Test case to verify the timeout value is set as expected
    """
    json = {"key": "value"}

    @parameterized.expand([
        ["test_int_value", {"request_timeout": 100}, 100.0],
        ["test_str_value", {"request_timeout": "100"}, 100.0],
        ["test_empty_value", {"request_timeout": ""}, 300.0],
        ["test_int_zero_value", {"request_timeout": 0}, 300.0],
        ["test_str_zero_value", {"request_timeout": "0"}, 300.0],
        ["test_no_value", {"request_timeout": "0"}, REQUEST_TIMEOUT]

    ])
    def test_timeout_value_in_config(self, mock_request, name, mock_config, expected_value):
        """
        Test if timeout value given in config
        """
        # mock response
        mock_request.return_value = get_response(200, self.json)

        test_client = OutreachClient(mock_config)

        # get the timeout value for assertion
        timeout = test_client.get_request_timeout(mock_config)
        test_client.request(method='get', url='')

        # verify that we got expected timeout value
        self.assertEqual(expected_value, timeout)
        # verify that the request was called with expected timeout value
        mock_request.assert_called_with('get', '', timeout=expected_value, headers={'Authorization': 'Bearer None'})



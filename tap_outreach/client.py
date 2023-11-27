import time
from datetime import datetime, timedelta

import backoff
import requests
import singer
from singer import metrics, utils

LOGGER = singer.get_logger()
REQUEST_TIMEOUT = 300

class Server5xxError(Exception):
    pass


class RateLimitError(Exception):
    pass


class OutreachClient():
    BASE_URL = 'https://api.outreach.io/api/v2/'

    def __init__(self, config):
        self.__user_agent = config.get('user_agent')
        self.__client_id = config.get('client_id')
        self.__client_secret = config.get('client_secret')
        self.__redirect_uri = config.get('redirect_uri')
        self.__refresh_token = config.get('refresh_token')
        self.__quota_limit = config.get('quota_limit')
        self.__access_token = None
        self.__expires_at = None
        self.__session = requests.Session()

        # Get the value of request timeout from config
        config_request_timeout = config.get('request_timeout')
        # Only set the timeout value if it is passed in the config and the value is not 0, "0" or ""
        if config_request_timeout and float(config_request_timeout):
            self.request_timeout = float(config_request_timeout)
        else:
            # Set default timeout
            self.request_timeout = REQUEST_TIMEOUT

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.__session.close()

    def refresh(self):
        resp = self.__session.request(
            'POST',
            url='https://api.outreach.io/oauth/token',
            data={
                'client_id': self.__client_id,
                'client_secret': self.__client_secret,
                'redirect_uri': self.__redirect_uri,
                'refresh_token': self.__refresh_token,
                'grant_type': 'refresh_token'
            })
        data = resp.json()

        self.__access_token = data['access_token']

        self.__expires_at = datetime.utcnow() + \
            timedelta(seconds=data['expires_in'] -
                      10)  # pad by 10 seconds for clock drift
        LOGGER.info(f"Refreshed access token, expires at {self.__expires_at}")

    @staticmethod
    def sleep_for_reset_period(response):
        reset = datetime.fromtimestamp(
            int(response.headers['x-ratelimit-reset']))
        sleep_time = (reset - datetime.now()).total_seconds() + \
            10  # pad for clock drift/sync issues
        LOGGER.warning(
            'Sleeping for {:.2f} seconds for next rate limit window'.format(sleep_time))
        time.sleep(sleep_time)

    @backoff.on_exception(backoff.expo,
                          (Server5xxError, RateLimitError, ConnectionError),
                          max_tries=5,
                          factor=3)
    # Rate Limit: https://api.outreach.io/api/v2/docs#rate-limiting
    @utils.ratelimit(10000, 3600)
    def request(self, method, path=None, url=None, skip_quota=False, **kwargs):
        if  (self.__access_token is None or
             self.__expires_at <= datetime.utcnow()):
            self.refresh()
        else:
            LOGGER.info("access_token is still valid; not refreshing")

        if url is None and path:
            url = '{}{}'.format(self.BASE_URL, path)

        if 'endpoint' in kwargs:
            endpoint = kwargs['endpoint']
            del kwargs['endpoint']
        else:
            endpoint = None

        if 'headers' not in kwargs:
            kwargs['headers'] = {}

        kwargs['headers']['Authorization'] = 'Bearer {}'.format(
            self.__access_token)

        if self.__user_agent:
            kwargs['headers']['User-Agent'] = self.__user_agent

        with metrics.http_request_timer(endpoint) as timer:
            response = self.__session.request(method, url, timeout=self.request_timeout, **kwargs)
            timer.tags[metrics.Tag.http_status_code] = response.status_code

        if response.status_code >= 500:
            raise Server5xxError(response.text)

        if response.status_code == 429:
            LOGGER.warning('Rate limit hit - 429')
            self.sleep_for_reset_period(response)
            raise RateLimitError()

        response.raise_for_status()

        if not skip_quota and self.__quota_limit:
            # x-rate-limit-remaining now appears to return two distinct ratelimit values, which are not yet documented
            # eg '9999, 19988'
            # based on default hourly-user limits, we believe the first value is the hourly limit remaining
            ratelimitrem = response.headers['x-ratelimit-remaining'].split(", ")[0]
            quota_used = 1 - int(ratelimitrem) / \
                int(ratelimitrem)
            if quota_used > float(self.__quota_limit):
                LOGGER.warning(
                    'Quota used: {:.2f} / {}'.format(quota_used, self.__quota_limit))
                self.sleep_for_reset_period(response)

        return response.json()

    def get(self, url=None, path=None, **kwargs):
        return self.request('GET', url=url, path=path, **kwargs)

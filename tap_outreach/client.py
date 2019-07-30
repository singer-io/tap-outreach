from datetime import datetime, timedelta

import backoff
import requests
from requests.exceptions import ConnectionError
from singer import metrics

class Server5xxError(Exception):
    pass

class OutreachClient(object):
    BASE_URL = 'https://api.outreach.io/api/v2/'

    def __init__(self, config):
        self.__user_agent = config.get('user_agent')
        self.__client_id = config.get('client_id')
        self.__client_secret = config.get('client_secret')
        self.__redirect_uri = config.get('redirect_uri')
        self.__refresh_token = config.get('refresh_token')
        self.__access_token = None
        self.__expires_at = None
        self.__session = requests.Session()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.__session.close()

    def refresh(self):
        data = self.request(
            'POST',
            url='https://api.outreach.io/oauth/token',
            data={
                'client_id': self.__client_id,
                'client_secret': self.__client_secret,
                'redirect_uri': self.__redirect_uri,
                'refresh_token': self.__refresh_token,
                'grant_type': 'refresh_token'
            })

        self.__access_token = data['access_token']

        self.__expires_at = datetime.utcnow() + \
            timedelta(seconds=data['expires_in'] - 10) # pad by 10 seconds for clock drift

    @backoff.on_exception(backoff.expo,
                          (Server5xxError, ConnectionError),
                          max_tries=5,
                          factor=2)
    def request(self, method, path=None, url=None, **kwargs):
        if url is None and \
            (self.__access_token is None or \
             self.__expires_at <= datetime.utcnow()):
            self.refresh()

        if url is None and path:
            url = '{}{}'.format(self.BASE_URL, path)

        if 'endpoint' in kwargs:
            endpoint = kwargs['endpoint']
            del kwargs['endpoint']
        else:
            endpoint = None

        if 'headers' not in kwargs:
            kwargs['headers'] = {}

        kwargs['headers']['Authorization'] = 'Bearer {}'.format(self.__access_token)

        if self.__user_agent:
            kwargs['headers']['User-Agent'] = self.__user_agent

        with metrics.http_request_timer(endpoint) as timer:
            response = self.__session.request(method, url, **kwargs)
            timer.tags[metrics.Tag.http_status_code] = response.status_code

        if response.status_code >= 500:
            raise Server5xxError()

        response.raise_for_status()

        return response.json()

    def get(self, path, **kwargs):
        return self.request('GET', path=path, **kwargs)

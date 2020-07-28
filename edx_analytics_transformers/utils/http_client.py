"""
A generic HTTP Client.
"""
import requests


class HttpClient:
    """
    A generic HTTP Client.
    """
    def __init__(
        self,
        host='',
        auth_scheme='',
        api_key='',
        headers=None,
    ):
        self.HOST = host
        self.AUTH_SCHEME = auth_scheme
        self.API_KEY = api_key
        self.HEADERS = headers or {}

    def get_auth_header(self):
        if self.AUTH_SCHEME:
            return {
                'Authorization': '{} {}'.format(self.AUTH_SCHEME, self.API_KEY)
            }
        return {}

    def send(self, json):
        headers = self.HEADERS.copy()
        headers.update(self.get_auth_header())
        return requests.post(self.HOST, json=json, headers=headers)

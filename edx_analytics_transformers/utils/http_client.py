"""
A generic HTTP Client.
"""
import requests


class HttpClient:
    """
    A generic HTTP Client.
    """
    def __init__(self, host='', auth_scheme='', api_key='', headers=None):
        """
        Initialize the client with provided configurations.

        host (str)        :     URL for the event consumer.
        auth_scheme (str) :     Scheme used for authentication.
        api_key (str)     :     API key used in the authorization header.
        headers (str)     :     Any additional headers to be sent with event payload.
        """
        self.HOST = host
        self.AUTH_SCHEME = auth_scheme
        self.API_KEY = api_key
        self.HEADERS = headers or {}

    def get_auth_header(self):
        """
        Generate auth headers depending upon the client configurations.
        """
        if self.AUTH_SCHEME:
            return {
                'Authorization': '{} {}'.format(self.AUTH_SCHEME, self.API_KEY)
            }
        return {}

    def send(self, json):
        """
        Send the event to configured remote.

        Arguments:
            json (dict) :   event payload to send to host.
        """
        headers = self.HEADERS.copy()
        headers.update(self.get_auth_header())
        return requests.post(self.HOST, json=json, headers=headers)

import time
from functools import wraps
from http import HTTPStatus

import requests


class AuthenticationError(Exception): ...


class TemplatingUnavailable(Exception): ...

class TemplatingAPI:

    def __init__(self, auth_server_url: str, templating_client_id: str, templating_client_secret: str):
        self.templating_client_id = templating_client_id
        self.templating_client_secret = templating_client_secret
        self.auth_server_url = auth_server_url
        self._token = None
        self._token_expiration_date = None

    @property
    def token(self) -> str:

        if self._token is None or time.time() > self._token_expiration_date:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }

            payload = {
                "client_id": self.templating_client_id,
                "client_secret": self.templating_client_secret,
                "grant_type": "client_credentials"
            }

            try:
                response = requests.post(self.auth_server_url,
                                         headers=headers,
                                         data=payload)
            except ConnectionError as e:
                raise TemplatingUnavailable(e)
            
            if response.status_code != HTTPStatus.OK:
                raise AuthenticationError(response.status_code, response.text)

            json_response = response.json()
            self._token = str(json_response['access_token'])
            self._token_expiration_date = time.time() + int(json_response['expires_in'])

        return self._token

    @property
    def header(self):
        header = {
            "Authorization": f"Bearer {self.token}",
        }
        return header

    @property
    def json_header(self):
        header = self.header
        header["Content-Type"] = "application/json"
        return header

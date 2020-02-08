import time
from functools import wraps
from http import HTTPStatus
from typing import NamedTuple, Sequence

import requests


class AuthenticationError(Exception): ...


class TemplatingUnavailable(Exception): ...


class TemplatingError(Exception): ...


def catch_connection_error(f):

    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ConnectionError as e:
            raise TemplatingUnavailable(e)
    return wrapper


class TemplateInfo(NamedTuple):
    """
    Template
    ---
    properties:
        template_id:
            type: string
            description: template id
        template_schema:
            type: object
            description: jsonschema for template
        type:
            type: string
            description: template MIME type
        metadata:
            type: object
            description: a collection on property values defined by the resource owner at the template conception
    """
    template_id: str
    template_schema: dict
    type: str
    metadata: dict


class TemplatingAPI:

    def __init__(
            self,
            auth_server_url: str,
            auth_scope: str,
            auth_id: str,
            auth_secret: str,
            templating_server_url: str
    ):
        self.auth_id = auth_id
        self.auth_secret = auth_secret
        self.auth_scope = auth_scope
        self.auth_server_url = auth_server_url
        self.templating_server_url = templating_server_url
        self._token = None
        self._token_expiration_date = None

    @property
    def token(self) -> str:

        if self._token is None or time.time() > self._token_expiration_date:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }

            payload = {
                "client_id": self.auth_id,
                "client_secret": self.auth_secret,
                "grant_type": "client_credentials",
                "scope": self.auth_scope
            }

            response = requests.post(self.auth_server_url,
                                     headers=headers,
                                     data=payload)

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

    @catch_connection_error
    def templates(self) -> Sequence[TemplateInfo]:

        response = requests.get(f"{self.templating_server_url}/templates/",
                                headers=self.header
                                )

        if response.status_code != HTTPStatus.OK:
            raise TemplatingError(response.status_code, response.text)

        templates = [TemplateInfo(**template_dict) for template_dict in response.json()]

        return templates

    @catch_connection_error
    def template(self, template_id: str) -> TemplateInfo:

        response = requests.get(f"{self.templating_server_url}/templates/{template_id}",
                                headers=self.header
                                )

        if response.status_code != HTTPStatus.OK:
            raise TemplatingError(response.status_code, response.text)

        template = TemplateInfo(**response.json())

        return template

    @catch_connection_error
    def compose(self, template_id: str, compose_data: dict, composed_file_target: str):

        response = requests.post(f"{self.templating_server_url}/template/{template_id}/compose",
                                 headers=self.json_header,
                                 json=compose_data
                                 )

        if response.status_code != HTTPStatus.CREATED:
            raise TemplatingError(response.status_code, response.text)

        with open(composed_file_target, mode='wb') as output:
            output.write(response.content)

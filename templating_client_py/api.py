import time
from functools import wraps
from http import HTTPStatus
from typing import NamedTuple, Sequence, Dict, List, Optional

import requests

from templating_client_py.request_collections import RequestDict


class AuthenticationError(Exception):
    """
    Error to be raised when something goes wrong with authentication.
    """
    ...


class TemplatingUnavailable(Exception):
    """
    Error to be raised when the API is unavailable.
    """
    ...


class TemplatingError(Exception):
    """
    Error to be raised when the API responds but not as expected.
    """
    ...


def catch_connection_error(f):
    """
    Simple decorator to catch when the connection for templating service fails and raises a TemplatingUnavailable.
    """
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
        tags:
            type: array
            items:
                type: string
    """
    template_id: str
    template_schema: dict
    type: str
    metadata: dict
    tags: List[str]


class TemplatingClient:
    """
    Templating client for the vizidox templating microservice.
    Takes care of authentication and everything on the background.

    Attributes:
        auth_server_url: The token endpoint where to request the token for templating access
        auth_scope: The OAUTH2 scope to include in the auth request to get access to the API
        auth_id: Your client id
        auth_secret: Your client secret
        templating_server_url: The url for the templating microservice.
    """
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
        """
        The current JWT token for API access.
        On access it checks if the previous one expired and renews it automatically if so.
        :return: the JWT token
        """
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
    def header(self) -> Dict[str, str]:
        """
        Authorization header to be used in API requests. Accesses self.token which may renew the token if needed.
        :return: header dict with 'Authorization' entry set with token.
        """
        header = {
            "Authorization": f"Bearer {self.token}",
        }
        return header

    @property
    def json_header(self) -> Dict[str, str]:
        """
        Authorization header to be used in API requests. Accesses self.token which may renew the token if needed.
        Also sets json header in request.
        :return: header dict with 'Authorization' and 'Content-type' entry set.
        """
        header = self.header
        header["Content-Type"] = "application/json"
        return header

    @catch_connection_error
    def templates(self, tags: List[str]) -> Sequence[TemplateInfo]:
        """
        Retrieves your templates from the API.
        :param tags: tags to filter the templates by
        :return: Sequence[TemplateInfo] on all the templates available
        """

        params = dict()

        if tags:
            params["tags"] = tags

        response = requests.get(f"{self.templating_server_url}/templates/",
                                headers=self.header,
                                params=params
                                )

        if response.status_code != HTTPStatus.OK:
            raise TemplatingError(response.status_code, response.text)

        templates = [TemplateInfo(**template_dict) for template_dict in response.json()]

        return templates

    @catch_connection_error
    def template(self, template_id: str) -> TemplateInfo:
        """
        Retrieves the template info with the given id.
        :param template_id: the template id
        :return: TemplateInfo on the template
        """
        response = requests.get(f"{self.templating_server_url}/templates/{template_id}",
                                headers=self.header
                                )

        if response.status_code != HTTPStatus.OK:
            raise TemplatingError(response.status_code, response.text)

        template = TemplateInfo(**response.json())

        return template

    @catch_connection_error
    def compose(self, template_id: str,
                compose_data: dict,
                mime_type="application/pdf",
                resize_height: Optional[int] = None,
                resize_width: Optional[int] = None
                ) -> bytes:
        """
        Makes a request for the template to be composed and returns the bytes for the file
        :param template_id: the template id
        :param compose_data: dict to compose template with
        :param mime_type: MIME type for the example
        :param resize_width: The height for resizing the template
        :param resize_height: The width for resizing the template
        """
        headers = {**self.json_header, **{"accept": mime_type}}
        query_params = RequestDict(height=resize_height, width=resize_width)
        response = requests.post(f"{self.templating_server_url}/template/{template_id}/compose",
                                 headers=headers,
                                 json=compose_data,
                                 params=query_params
                                 )

        if response.status_code != HTTPStatus.OK:
            raise TemplatingError(response.status_code, response.text)

        return response.content

    @catch_connection_error
    def template_example(self, template_id: str,
                         mime_type="application/pdf",
                         resize_height: Optional[int] = None,
                         resize_width: Optional[int] = None) -> bytes:
        """
        Makes a request for the template to be composed and returns the bytes for the file
        :param template_id: the template id
        :param mime_type: MIME type for the example
        :param resize_width: The height for resizing the template
        :param resize_height: The width for resizing the template
        """
        headers = {**self.header, **{"accept": mime_type}}
        query_params = RequestDict(height=resize_height, width=resize_width)

        response = requests.get(f"{self.templating_server_url}/template/{template_id}/example",
                                headers=headers,
                                params=query_params
                                )

        if response.status_code != HTTPStatus.OK:
            raise TemplatingError(response.status_code, response.text)

        return response.content

    def compose_to_file(self, template_id: str, compose_data: dict, composed_file_target: str, *args, **kwargs):
        """
        Makes a request for the template to be composed and writes the result to a file.
        :param template_id: the template id
        :param compose_data: dict to compose template with
        :param composed_file_target: path to file to be written. Caution: file is overwritten
        :param args: extra arguments to send to compose
        :param kwargs: extra keyword arguments to send to compose
        """
        composed_content = self.compose(template_id, compose_data, *args, **kwargs)

        with open(composed_file_target, mode='wb') as output:
            output.write(composed_content)

import json
from functools import wraps
from http import HTTPStatus
from typing import NamedTuple, Sequence, List, Optional, BinaryIO, Callable, TypeVar, Any, cast

import backoff
import requests

from plato_helper_py.request_collections import RequestDict

DEFAULT_TIMEOUT = 10

F = TypeVar('F', bound=Callable[..., Any])


class PlatoUnavailable(Exception):
    """
    Error to be raised when the API is unavailable.
    """


class PlatoError(Exception):
    """
    Error to be raised when the API responds but not as expected.
    """


def catch_connection_error(f: F) -> F:
    """
    Decorator to catch when the connection for Plato templating service fails and raises a PlatoUnavailable.

    The call_plato method allows the use of the backoff decorator to retry the plato call several times when a
    Connection Error occurs.

    It is assumed that we are decorating a method of the PlatoHelper class, which contains the max_tries field to
    determine the maximum numer of attempts to resend requests. Since the first argument is always the PlatoHelper
    instance (self), we can safely access the max_tries field directly.

    :param f: decorated function
    :type f: Callable

    :return: The decorator function
    :rtype: F
    """
    @wraps(f)
    def wrapper(plato_helper: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Wrapper function for the decorator.

        :param plato_helper: The Plato Helper instance
        :type plato_helper: Any

        :param args: The arguments of the function
        :type args: List[Any]

        :param kwargs: The keyword arguments of the function
        :type kwargs: Dict[str, Any]

        :return: The function return, or an error message
        :rtype: Any
        """

        @backoff.on_exception(wait_gen=backoff.expo, exception=ConnectionError, max_tries=plato_helper.max_tries)
        def call_plato_method() -> Any:
            """
            Call the decorated method, which is assumed to be a method of the PlatoHelper class.

            :return: The function return
            :rtype: Any
            """
            return f(plato_helper, *args, **kwargs)

        try:
            return call_plato_method()
        except ConnectionError as e:
            raise PlatoUnavailable(e) from e
    return cast(F, wrapper)


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


class PlatoHelper:
    """
    Plato helper for Plato

    Attributes:
        plato_host: The host for the Plato microservice
        max_tries: Number of retries the helper attempts when a ConnectionError is raised
    """

    def __init__(self, plato_host: str, max_tries: int = 3):
        self.plato_host = plato_host
        self.max_tries = max_tries

    @catch_connection_error
    def templates(self, tags: List[str]) -> Sequence[TemplateInfo]:
        """
        Retrieves your templates from the API.

        :param tags: Tags to filter the templates by
        :type tags: List[str]

        :return: Sequence[TemplateInfo] on all the templates available
        :rtype: Sequence[TemplateInfo]
        """
        params = {}

        if tags:
            params["tags"] = tags

        response = requests.get(f"{self.plato_host}/templates/",
                                params=params,
                                timeout=DEFAULT_TIMEOUT
                                )

        if response.status_code != HTTPStatus.OK:
            raise PlatoError(response.status_code, response.text)

        return [TemplateInfo(**template_dict) for template_dict in response.json()]

    @catch_connection_error
    def template(self, template_id: str) -> TemplateInfo:
        """
        Retrieves the template info with the given id.

        :param template_id: the template id
        :type template_id: str

        :return: TemplateInfo on the template
        :rtype: TemplateInfo
        """
        response = requests.get(f"{self.plato_host}/templates/{template_id}",
                                timeout=DEFAULT_TIMEOUT
                                )

        if response.status_code != HTTPStatus.OK:
            raise PlatoError(response.status_code, response.text)

        return TemplateInfo(**response.json())

    @catch_connection_error
    def compose(self, template_id: str,
                compose_data: dict,
                mime_type: str = "application/pdf",
                page: Optional[int] = None,
                resize_height: Optional[int] = None,
                resize_width: Optional[int] = None
                ) -> bytes:
        """
        Makes a request for the template to be composed and returns the bytes for the file.

        :param template_id: The template id
        :type template_id: str

        :param compose_data: Dictionary to compose template with
        :type compose_data: dict

        :param mime_type: MIME type for the example
        :type mime_type: str

        :param page: The number of the page to be printed
        :type page: Optional[int]

        :param resize_width: The height for resizing the template
        :type resize_width: Optional[int]

        :param resize_height: The width for resizing the template
        :type resize_height: Optional[int]

        :return: Bytes for the composed file
        :rtype: bytes
        """
        headers = {**{"accept": mime_type}}
        query_params = RequestDict(page=page, height=resize_height, width=resize_width)
        response = requests.post(f"{self.plato_host}/template/{template_id}/compose",
                                 headers=headers,
                                 json=compose_data,
                                 params=query_params,
                                 timeout=DEFAULT_TIMEOUT
                                 )

        if response.status_code != HTTPStatus.OK:
            raise PlatoError(response.status_code, response.text)

        return response.content

    @catch_connection_error
    def template_example(self, template_id: str,
                         mime_type: str = "application/pdf",
                         page: Optional[int] = None,
                         resize_height: Optional[int] = None,
                         resize_width: Optional[int] = None) -> bytes:
        """
        Makes a request for the template to be composed and returns the bytes for the file.

        :param template_id: The template id
        :type template_id: str

        :param mime_type: MIME type for the example
        :type mime_type: str

        :param page: The number of the page to be printed
        :type page: Optional[int]

        :param resize_width: The height for resizing the template
        :type resize_width: Optional[int]

        :param resize_height: The width for resizing the template
        :type resize_height: Optional[int]
        """
        headers = {**{"accept": mime_type}}
        query_params = RequestDict(page=page, height=resize_height, width=resize_width)

        response = requests.get(f"{self.plato_host}/template/{template_id}/example",
                                headers=headers,
                                params=query_params,
                                timeout=DEFAULT_TIMEOUT
                                )

        if response.status_code != HTTPStatus.OK:
            raise PlatoError(response.status_code, response.text)

        return response.content

    @catch_connection_error
    def create_template(self, file_stream: BinaryIO, template_details: dict) -> TemplateInfo:
        """
        Creates new template.

        :param file_stream: The file stream
        :type file_stream: BinaryIO

        :param template_details: The template details
        :type template_details: dict

        :return: TemplateInfo of the new template
        :rtype: TemplateInfo
        """
        file_stream.seek(0)
        template_details_str = json.dumps(template_details)

        data = RequestDict(zipfile=file_stream, template_details=template_details_str)

        response = requests.post(f"{self.plato_host}/template/create",
                                 data=data,
                                 timeout=DEFAULT_TIMEOUT
                                 )

        if response.status_code != HTTPStatus.CREATED:
            raise PlatoError(response.status_code, response.text)

        return TemplateInfo(**response.json())

    @catch_connection_error
    def update_template(self, template_id: str, file_stream: BinaryIO, template_details: dict) -> TemplateInfo:
        """
        Updates template by template id.

        :param template_id: The template id
        :type template_id: str

        :param file_stream: The file stream
        :type file_stream: BinaryIO

        :param template_details: The template details
        :type template_details: dict

        :return: TemplateInfo of the updated template
        :rtype: TemplateInfo
        """
        file_stream.seek(0)

        template_details_str = json.dumps(template_details)
        data = RequestDict(zipfile=file_stream, template_details=template_details_str)

        response = requests.put(f"{self.plato_host}/template/{template_id}/update",
                                data=data,
                                timeout=DEFAULT_TIMEOUT
                                )

        if response.status_code != HTTPStatus.OK:
            raise PlatoError(response.status_code, response.text)

        return TemplateInfo(**response.json())

    @catch_connection_error
    def update_template_details(self, template_id: str, template_details: dict) -> TemplateInfo:
        """
        Updates template details by template id.

        :param template_id: The template id
        :type template_id: str

        :param template_details: The template details
        :type template_details: dict

        :return: TemplateInfo of the updated template
        :rtype: TemplateInfo
        """

        response = requests.patch(f"{self.plato_host}/template/{template_id}/update_details",
                                  json=template_details,
                                  timeout=DEFAULT_TIMEOUT
                                  )

        if response.status_code != HTTPStatus.OK:
            raise PlatoError(response.status_code, response.text)

        return TemplateInfo(**response.json())

    def compose_to_file(self, template_id: str, compose_data: dict, composed_file_target: str, *args: Any,
                        **kwargs: Any) -> None:
        """
        Makes a request for the template to be composed and writes the result to a file.

        :param template_id: The template id
        :type template_id: str

        :param compose_data: Dictionary to compose template with
        :type compose_data: dict

        :param composed_file_target: Path to file to be written. Caution: file is overwritten
        :type composed_file_target: str

        :param args: Extra arguments to send to compose
        :type args: Any

        :param kwargs: Extra keyword arguments to send to compose
        :type kwargs: Any
        """
        composed_content = self.compose(template_id, compose_data, *args, **kwargs)

        with open(composed_file_target, mode='wb') as output:
            output.write(composed_content)

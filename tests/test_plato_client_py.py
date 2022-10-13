import io
import json
from http import HTTPStatus
from tempfile import NamedTemporaryFile
from unittest import TestCase
from unittest.mock import patch, MagicMock

from plato_client_py import PlatoClient
from plato_client_py.api import PlatoUnavailable, PlatoError, DEFAULT_TIMEOUT
from tests.resources import templates_json, expected_templates, ranger_certificate_template, \
    ranger_certificate_schema

PLATO_HOST = "plato://localhost:5000"
MAX_TRIES = 5


class TestPlatoClient(TestCase):

    def setUp(self) -> None:
        self.plato_client = PlatoClient(PLATO_HOST, MAX_TRIES)
        self.compose_data = {"name": "Charlotte Pine", "course": "Forest Ranger Certification"}

    @patch('plato_client_py.api.requests')
    def test_get_templates(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = templates_json
        mock_requests.get.return_value = mock_response

        tag = ["certificate"]
        templates = self.plato_client.templates(tag)
        mock_requests.get.assert_called_with(f"{PLATO_HOST}/templates/", params={'tags': ['certificate']},
                                             timeout=DEFAULT_TIMEOUT)
        self.assertEqual(templates, expected_templates)

    @patch('plato_client_py.api.requests')
    def test_get_templates_empty_tag_param(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = templates_json
        mock_requests.get.return_value = mock_response

        tag = []
        templates = self.plato_client.templates(tag)
        mock_requests.get.assert_called_with(f"{PLATO_HOST}/templates/", params={}, timeout=DEFAULT_TIMEOUT)
        self.assertEqual(templates, expected_templates)

    @patch('plato_client_py.api.requests')
    def test_get_templates_connection_error(self, mock_requests):
        mock_requests.get.side_effect = ConnectionError()
        self.plato_client.max_tries = 1
        tag = ["certificate"]
        with self.assertRaises(PlatoUnavailable):
            self.plato_client.templates(tag)
        mock_requests.get.assert_called_with(f"{PLATO_HOST}/templates/", params={'tags': ['certificate']},
                                             timeout=DEFAULT_TIMEOUT)

    @patch('plato_client_py.api.requests')
    def test_get_templates_plato_error(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.BAD_REQUEST
        mock_response.text.return_value = "Bad Request"
        mock_requests.get.return_value = mock_response

        tag = ["certificate"]

        with self.assertRaises(PlatoError):
            self.plato_client.templates(tag)
        mock_requests.get.assert_called_with(f"{PLATO_HOST}/templates/", params={'tags': ['certificate']},
                                             timeout=DEFAULT_TIMEOUT)

    @patch('plato_client_py.api.requests')
    def test_get_template(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = ranger_certificate_template._asdict()
        mock_requests.get.return_value = mock_response

        template_id = "ranger_certificate"
        template = self.plato_client.template(template_id)
        mock_requests.get.assert_called_with(f"{PLATO_HOST}/templates/{template_id}", timeout=DEFAULT_TIMEOUT)
        self.assertEqual(template, ranger_certificate_template)

    @patch('plato_client_py.api.requests')
    def test_get_template_connection_error(self, mock_requests):
        mock_requests.get.side_effect = ConnectionError()
        self.plato_client.max_tries = 1
        template_id = "ranger_certificate"
        with self.assertRaises(PlatoUnavailable):
            self.plato_client.template(template_id)
        mock_requests.get.assert_called_with(f"{PLATO_HOST}/templates/{template_id}", timeout=DEFAULT_TIMEOUT)

    @patch('plato_client_py.api.requests')
    def test_get_template_plato_error(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.NOT_FOUND
        mock_response.text.return_value = "Not Found"
        mock_requests.get.return_value = mock_response
        template_id = "ranger_certificate"
        with self.assertRaises(PlatoError):
            self.plato_client.template(template_id)
        mock_requests.get.assert_called_with(f"{PLATO_HOST}/templates/{template_id}", timeout=DEFAULT_TIMEOUT)

    @patch('plato_client_py.api.requests')
    def test_compose_template(self, mock_requests):
        expected_file = bytes('Simple certificate', 'utf-8')
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = expected_file
        mock_requests.post.return_value = mock_response

        template_id = "ranger_certificate"
        file = self.plato_client.compose(template_id=template_id, compose_data=self.compose_data)
        mock_requests.post.assert_called_with(f"{PLATO_HOST}/template/{template_id}/compose",
                                              headers={'accept': 'application/pdf'},
                                              json=self.compose_data, params={}, timeout=DEFAULT_TIMEOUT)
        self.assertEqual(file, expected_file)

    @patch('plato_client_py.api.requests')
    def test_compose_template_with_optional_params(self, mock_requests):
        expected_file = bytes('Simple certificate', 'utf-8')
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = expected_file
        mock_requests.post.return_value = mock_response

        template_id = "ranger_certificate"
        # all optional params
        file = self.plato_client.compose(template_id=template_id, compose_data=self.compose_data, mime_type="image/png",
                                         page=1, resize_height=100, resize_width=100)
        mock_requests.post.assert_called_with(f"{PLATO_HOST}/template/{template_id}/compose",
                                              headers={'accept': 'image/png'},
                                              json=self.compose_data, params={'page': 1, 'height': 100, 'width': 100},
                                              timeout=DEFAULT_TIMEOUT)
        self.assertEqual(file, expected_file)

        # only one optional param
        file = self.plato_client.compose(template_id=template_id, compose_data=self.compose_data, mime_type="image/png",
                                         page=1)
        mock_requests.post.assert_called_with(f"{PLATO_HOST}/template/{template_id}/compose",
                                              headers={'accept': 'image/png'},
                                              json=self.compose_data, params={'page': 1},
                                              timeout=DEFAULT_TIMEOUT)
        self.assertEqual(file, expected_file)

    @patch('plato_client_py.api.requests')
    def test_compose_template_connection_error(self, mock_requests):
        mock_requests.post.side_effect = ConnectionError()
        self.plato_client.max_tries = 1

        template_id = "ranger_certificate"
        with self.assertRaises(PlatoUnavailable):
            file = self.plato_client.compose(template_id=template_id, compose_data=self.compose_data)
            self.assertIsNone(file)
        mock_requests.post.assert_called_with(f"{PLATO_HOST}/template/{template_id}/compose",
                                              headers={'accept': 'application/pdf'},
                                              json=self.compose_data, params={}, timeout=DEFAULT_TIMEOUT)

    @patch('plato_client_py.api.requests')
    def test_compose_template_plato_error(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.NOT_FOUND
        mock_response.text.return_value = "Not Found"
        mock_requests.post.return_value = mock_response

        template_id = "ranger_certificate"
        with self.assertRaises(PlatoError):
            file = self.plato_client.compose(template_id=template_id, compose_data=self.compose_data)
            self.assertIsNone(file)

        mock_requests.post.assert_called_with(f"{PLATO_HOST}/template/{template_id}/compose",
                                              headers={'accept': 'application/pdf'},
                                              json=self.compose_data, params={}, timeout=DEFAULT_TIMEOUT)

    @patch('plato_client_py.api.requests')
    def test_template_example(self, mock_requests):
        expected_file = bytes('Simple certificate', 'utf-8')
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = expected_file
        mock_requests.get.return_value = mock_response

        template_id = "ranger_certificate"
        file = self.plato_client.template_example(template_id=template_id)
        mock_requests.get.assert_called_with(f"{PLATO_HOST}/template/{template_id}/example",
                                             headers={'accept': 'application/pdf'}, params={}, timeout=DEFAULT_TIMEOUT)
        self.assertEqual(file, expected_file)

    @patch('plato_client_py.api.requests')
    def test_template_example_with_optional_params(self, mock_requests):
        expected_file = bytes('Simple certificate', 'utf-8')
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = expected_file
        mock_requests.get.return_value = mock_response

        template_id = "ranger_certificate"
        # all optional params
        file = self.plato_client.template_example(template_id=template_id, mime_type="image/png",
                                                  page=1, resize_height=100, resize_width=100)
        mock_requests.get.assert_called_with(f"{PLATO_HOST}/template/{template_id}/example",
                                             headers={'accept': 'image/png'},
                                             params={'page': 1, 'height': 100, 'width': 100},
                                             timeout=DEFAULT_TIMEOUT)
        self.assertEqual(file, expected_file)

        # only one optional param
        file = self.plato_client.template_example(template_id=template_id, mime_type="image/png", page=1)
        mock_requests.get.assert_called_with(f"{PLATO_HOST}/template/{template_id}/example",
                                             headers={'accept': 'image/png'},
                                             params={'page': 1},
                                             timeout=DEFAULT_TIMEOUT)
        self.assertEqual(file, expected_file)

    @patch('plato_client_py.api.requests')
    def test_template_example_connection_error(self, mock_requests):
        mock_requests.get.side_effect = ConnectionError()
        self.plato_client.max_tries = 1

        template_id = "ranger_certificate"
        with self.assertRaises(PlatoUnavailable):
            file = self.plato_client.template_example(template_id=template_id)
            self.assertIsNone(file)
        mock_requests.get.assert_called_with(f"{PLATO_HOST}/template/{template_id}/example",
                                             headers={'accept': 'application/pdf'},
                                             params={}, timeout=DEFAULT_TIMEOUT)

    @patch('plato_client_py.api.requests')
    def test_template_example_plato_error(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.NOT_FOUND
        mock_response.text.return_value = "Not Found"
        mock_requests.get.return_value = mock_response

        template_id = "ranger_certificate"
        with self.assertRaises(PlatoError):
            file = self.plato_client.template_example(template_id=template_id)
            self.assertIsNone(file)

        mock_requests.get.assert_called_with(f"{PLATO_HOST}/template/{template_id}/example",
                                             headers={'accept': 'application/pdf'},
                                             params={}, timeout=DEFAULT_TIMEOUT)

    @patch('plato_client_py.api.requests')
    def test_create_template(self, mock_requests):
        file = io.BytesIO()
        file.write(b'hello')
        self.assertEqual(file.tell(), 5)

        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.CREATED
        mock_response.json.return_value = ranger_certificate_template._asdict()
        mock_requests.post.return_value = mock_response

        template = self.plato_client.create_template(file_stream=file, template_details=ranger_certificate_schema)
        mock_requests.post.assert_called_with(f"{PLATO_HOST}/template/create",
                                              data={'zipfile': file, 'template_details':
                                                    json.dumps(ranger_certificate_schema)},
                                              timeout=DEFAULT_TIMEOUT)
        self.assertEqual(file.tell(), 0)
        self.assertEqual(template, ranger_certificate_template)

        # empty dict
        template = self.plato_client.create_template(file_stream=file, template_details={})
        mock_requests.post.assert_called_with(f"{PLATO_HOST}/template/create",
                                              data={'zipfile': file, 'template_details': '{}'},
                                              timeout=DEFAULT_TIMEOUT)
        self.assertEqual(file.tell(), 0)
        self.assertEqual(template, ranger_certificate_template)

    @patch('plato_client_py.api.requests')
    def test_create_template_connection_error(self, mock_requests):
        file = io.BytesIO()
        file.write(b'hello')

        mock_requests.post.side_effect = ConnectionError()
        self.plato_client.max_tries = 1

        with self.assertRaises(PlatoUnavailable):
            template = self.plato_client.create_template(file_stream=file, template_details=ranger_certificate_schema)
            self.assertIsNone(template)
        mock_requests.post.assert_called_with(f"{PLATO_HOST}/template/create",
                                              data={'zipfile': file,
                                                    'template_details': json.dumps(ranger_certificate_schema)},
                                              timeout=DEFAULT_TIMEOUT)

    @patch('plato_client_py.api.requests')
    def test_create_template_plato_error(self, mock_requests):
        file = io.BytesIO()
        file.write(b'hello')
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.NOT_FOUND
        mock_response.text.return_value = "Not Found"
        mock_requests.post.return_value = mock_response

        with self.assertRaises(PlatoError):
            template = self.plato_client.create_template(file_stream=file, template_details=ranger_certificate_schema)
            self.assertIsNone(template)

        mock_requests.post.assert_called_with(f"{PLATO_HOST}/template/create",
                                              data={'zipfile': file,
                                                    'template_details': json.dumps(ranger_certificate_schema)},
                                              timeout=DEFAULT_TIMEOUT)

    @patch('plato_client_py.api.requests')
    def test_update_template(self, mock_requests):
        file = io.BytesIO()
        file.write(b'hello')
        self.assertEqual(file.tell(), 5)

        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = ranger_certificate_template._asdict()
        mock_requests.put.return_value = mock_response

        template_id = "ranger_certificate"
        template = self.plato_client.update_template(template_id=template_id, file_stream=file,
                                                     template_details=ranger_certificate_schema)
        mock_requests.put.assert_called_with(f"{PLATO_HOST}/template/{template_id}/update",
                                             data={'zipfile': file, 'template_details':
                                                   json.dumps(ranger_certificate_schema)},
                                             timeout=DEFAULT_TIMEOUT)
        self.assertEqual(file.tell(), 0)
        self.assertEqual(template, ranger_certificate_template)

        # empty dict
        template = self.plato_client.update_template(template_id=template_id, file_stream=file,
                                                     template_details={})
        mock_requests.put.assert_called_with(f"{PLATO_HOST}/template/{template_id}/update",
                                             data={'zipfile': file, 'template_details': '{}'},
                                             timeout=DEFAULT_TIMEOUT)
        self.assertEqual(file.tell(), 0)
        self.assertEqual(template, ranger_certificate_template)

    @patch('plato_client_py.api.requests')
    def test_update_template_connection_error(self, mock_requests):
        file = io.BytesIO()
        file.write(b'hello')

        mock_requests.put.side_effect = ConnectionError()
        self.plato_client.max_tries = 1

        template_id = "ranger_certificate"
        with self.assertRaises(PlatoUnavailable):
            template = self.plato_client.update_template(template_id=template_id, file_stream=file,
                                                         template_details=ranger_certificate_schema)
            self.assertIsNone(template)
        mock_requests.put.assert_called_with(f"{PLATO_HOST}/template/{template_id}/update",
                                             data={'zipfile': file,
                                                   'template_details': json.dumps(ranger_certificate_schema)},
                                             timeout=DEFAULT_TIMEOUT)

    @patch('plato_client_py.api.requests')
    def test_update_template_plato_error(self, mock_requests):
        file = io.BytesIO()
        file.write(b'hello')
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.NOT_FOUND
        mock_response.text.return_value = "Not Found"
        mock_requests.put.return_value = mock_response

        template_id = "ranger_certificate"
        with self.assertRaises(PlatoError):
            template = self.plato_client.update_template(template_id=template_id, file_stream=file,
                                                         template_details=ranger_certificate_schema)
            self.assertIsNone(template)

        mock_requests.put.assert_called_with(f"{PLATO_HOST}/template/{template_id}/update",
                                             data={'zipfile': file,
                                                   'template_details': json.dumps(ranger_certificate_schema)},
                                             timeout=DEFAULT_TIMEOUT)

    @patch('plato_client_py.api.requests')
    def test_update_template_details(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.json.return_value = ranger_certificate_template._asdict()
        mock_requests.patch.return_value = mock_response

        template_id = "ranger_certificate"
        template = self.plato_client.update_template_details(template_id=template_id,
                                                             template_details=ranger_certificate_schema)
        mock_requests.patch.assert_called_with(f"{PLATO_HOST}/template/{template_id}/update_details",
                                               json=ranger_certificate_schema,
                                               timeout=DEFAULT_TIMEOUT)
        self.assertEqual(template, ranger_certificate_template)

        # empty dict
        template = self.plato_client.update_template_details(template_id=template_id,
                                                             template_details={})
        mock_requests.patch.assert_called_with(f"{PLATO_HOST}/template/{template_id}/update_details",
                                               json={},
                                               timeout=DEFAULT_TIMEOUT)
        self.assertEqual(template, ranger_certificate_template)

    @patch('plato_client_py.api.requests')
    def test_update_template_details_connection_error(self, mock_requests):
        mock_requests.patch.side_effect = ConnectionError()
        self.plato_client.max_tries = 1

        template_id = "ranger_certificate"
        with self.assertRaises(PlatoUnavailable):
            template = self.plato_client.update_template_details(template_id=template_id,
                                                                 template_details=ranger_certificate_schema)
            self.assertIsNone(template)
        mock_requests.patch.assert_called_with(f"{PLATO_HOST}/template/{template_id}/update_details",
                                               json=ranger_certificate_schema,
                                               timeout=DEFAULT_TIMEOUT)

    @patch('plato_client_py.api.requests')
    def test_update_template_details_plato_error(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.NOT_FOUND
        mock_response.text.return_value = "Not Found"
        mock_requests.patch.return_value = mock_response

        template_id = "ranger_certificate"
        with self.assertRaises(PlatoError):
            template = self.plato_client.update_template_details(template_id=template_id,
                                                                 template_details=ranger_certificate_schema)
            self.assertIsNone(template)

        mock_requests.patch.assert_called_with(f"{PLATO_HOST}/template/{template_id}/update_details",
                                               json=ranger_certificate_schema,
                                               timeout=DEFAULT_TIMEOUT)

    @patch('plato_client_py.api.requests')
    def test_compose_to_file(self, mock_requests):
        expected_file = bytes('Simple certificate', 'utf-8')
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = expected_file
        mock_requests.post.return_value = mock_response

        template_id = "ranger_certificate"
        with NamedTemporaryFile(suffix='.pdf') as tmp_file:
            self.plato_client.compose_to_file(template_id=template_id, compose_data=self.compose_data,
                                              composed_file_target=tmp_file.name)

            mock_requests.post.assert_called_with(f"{PLATO_HOST}/template/{template_id}/compose",
                                                  headers={'accept': 'application/pdf'},
                                                  json=self.compose_data, params={}, timeout=DEFAULT_TIMEOUT)
            self.assertEqual(tmp_file.read(), expected_file)

    @patch('plato_client_py.api.requests')
    def test_compose_to_file_with_optional_params(self, mock_requests):
        expected_file = bytes('Simple certificate', 'utf-8')
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = expected_file
        mock_requests.post.return_value = mock_response
        template_id = "ranger_certificate"

        with NamedTemporaryFile(suffix='.pdf') as tmp_file:
            self.plato_client.compose_to_file(template_id=template_id, compose_data=self.compose_data,
                                              composed_file_target=tmp_file.name,
                                              **{'mime_type': 'application/pdf', 'page': 1,
                                                 'resize_height': 100, 'resize_width': 100})
            self.assertEqual(tmp_file.read(), expected_file)

        mock_requests.post.assert_called_with(f"{PLATO_HOST}/template/{template_id}/compose",
                                              headers={'accept': 'application/pdf'},
                                              json=self.compose_data, params={'page': 1,
                                                                              'height': 100,
                                                                              'width': 100},
                                              timeout=DEFAULT_TIMEOUT)

    @patch('plato_client_py.api.requests')
    def test_compose_to_file_with_wrong_params(self, mock_requests):
        expected_file = bytes('Simple certificate', 'utf-8')
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = expected_file
        mock_requests.post.return_value = mock_response
        template_id = "ranger_certificate"

        with self.assertRaises(TypeError):
            with NamedTemporaryFile(suffix='.pdf') as tmp_file:
                self.plato_client.compose_to_file(template_id=template_id, compose_data=self.compose_data,
                                                  composed_file_target=tmp_file.name,
                                                  **{'mime_type': 'application/pdf', 'page': 1, 'wrong_param': 'wrong'})
                self.assertEqual(tmp_file.read(), expected_file)
        mock_requests.post.assert_not_called()

    @patch('plato_client_py.api.requests')
    def test_compose_to_file_connection_error(self, mock_requests):
        mock_requests.post.side_effect = ConnectionError()
        self.plato_client.max_tries = 1
        template_id = "ranger_certificate"

        with self.assertRaises(PlatoUnavailable):
            with NamedTemporaryFile(suffix='.pdf') as tmp_file:
                initial_file = tmp_file
                self.plato_client.compose_to_file(template_id=template_id, compose_data=self.compose_data,
                                                  composed_file_target=tmp_file.name)
                self.assertEqual(initial_file, tmp_file)

        mock_requests.post.assert_called_with(f"{PLATO_HOST}/template/{template_id}/compose",
                                              headers={'accept': 'application/pdf'},
                                              json=self.compose_data, params={}, timeout=DEFAULT_TIMEOUT)

    @patch('plato_client_py.api.requests')
    def test_compose_to_file_plato_error(self, mock_requests):
        mock_response = MagicMock()
        mock_response.status_code = HTTPStatus.NOT_FOUND
        mock_response.text.return_value = "Not Found"
        mock_requests.post.return_value = mock_response

        template_id = "ranger_certificate"
        with self.assertRaises(PlatoError):
            with NamedTemporaryFile(suffix='.pdf') as tmp_file:
                initial_file = tmp_file
                self.plato_client.compose_to_file(template_id=template_id, compose_data=self.compose_data,
                                                  composed_file_target=tmp_file.name)
                self.assertEqual(initial_file, tmp_file)

        mock_requests.post.assert_called_with(f"{PLATO_HOST}/template/{template_id}/compose",
                                              headers={'accept': 'application/pdf'},
                                              json=self.compose_data, params={}, timeout=DEFAULT_TIMEOUT)

import requests
import json
from urllib.parse import urljoin
from robot.api import logger

from .version import VERSION

__version__ = VERSION


class WireMockLibrary(object):
    """Robot Framework library for interacting with [http://wiremock.org|WireMock]

    The purpose of this library is to provide a keyword-based API
    towards WireMock to be used in robot tests. The project is hosted in
    [https://github.com/tyrjola/robotframework-wiremock|GitHub],
    and packages are released to PyPI.

    = Installation =

    | pip install robotframework-wiremock

    = Importing =

    The library does not currently support any import arguments, so use the
    following setting to take the library into use:

    | Library | WireMockLibrary |

    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__

    def create_mock_session(self, base_url):
        """Creates an HTTP session towards wiremock.

        `base_url` is the full url (including port, if applicable) of the WireMock
        server, e.g. http://localhost:8080.
        """
        logger.debug("robotframework-wiremock libary version: {}".format(__version__))

        self.base_url = base_url
        self.session = requests.Session()

    def create_mock_request_matcher(self, method, url, json_body=None):
        """Creates a mock request matcher to be used by wiremock.

        Returns the request matcher in a dictionary format.

        `method` is the HTTP method of the mocked endpoint

        `url` is the url of the mocked endpoint, e.g. /api

        `json_body` is a dictionary of the json attribute(s) to match
        """
        req = {}
        req['method'] = method
        req['url'] = url

        if json_body:
            req['bodyPatterns'] = [{'equalToJson': json.dumps(json_body),
                                    'ignoreArrayOrder': True,
                                    'ignoreExtraElements': True}]

        return req

    def create_mock_response(self, status, headers=None, json_body=None):
        """Creates a mock response to be used by wiremock.

        Returns the response in a dictionary format.

        `status` is the HTTP status code of the response

        `headers` is a dictionary of headers to be added to the response

        `json_body` is a dictonary of JSON attribute(s) to be added to the response body
        """
        rsp = {}
        rsp['status'] = int(status)
        rsp['headers'] = headers

        if json_body:
            rsp['jsonBody'] = json_body

        return rsp

    def create_mock_mapping(self, request, response):
        """Creates an mapping to be used by wiremock.

        `request` is a mock request matcher in a dictionary format.

        `response` is a mock response in a dictionary format.
        """
        data = {}
        data['request'] = request
        data['response'] = response

        self.create_mock_mapping_with_data(data)

    def create_default_mock_mapping(self, method, url, status=200,
                                    response_headers=None, response_body=None):
        """Creates a default expectation to be used by wiremock.

        `method` is the HTTP method of the mocked endpoint

        `url` is the url of the mocked endpoint, e.g. /api

        `status` is the HTTP status code of the response

        `response_headers` is a dictionary of headers to be added to the response

        `response_body` is a dictonary of JSON attribute(s) to be added to the response body
        """
        req = self.create_mock_request_matcher(method, url)
        rsp = self.create_mock_response(status, response_headers, response_body)
        self.create_mock_mapping(req, rsp)

    def create_mock_mapping_with_data(self, data):
        """Creates a mapping with defined data to be used by wiremock.

        `data` is a dictionary or JSON string with mapping data. Please see
        [http://wiremock.org/docs/api/|WireMock documentation] for the detailed API reference.
        """
        self._send_request("/__admin/mappings", data)

    def reset_mock_mappings(self):
        """Resets all mock mappings on the wiremock server.
        """
        self._send_request("/__admin/mappings/reset")

    def _send_request(self, path, data=None):
        if isinstance(data, dict):
            data_dump = json.dumps(data)
        else:
            data_dump = data

        url = urljoin(self.base_url, path)

        logger.debug("url: {}, data: {}".format(url, data_dump))
        rsp = self.session.post(url, data=data_dump, timeout=5.0)

        if rsp.status_code >= 400:
            raise AssertionError("Wiremock failed with {}: {}".format(rsp.status_code, rsp.text))

        return rsp

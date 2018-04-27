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

    def create_mock_request_matcher(self, method, url, url_match_type='urlPath',
                                    query_parameters=None, headers=None, cookies=None,
                                    json_body=None, regex_matching=False):
        """Creates a mock request matcher to be used by wiremock.

        Returns the request matcher in a dictionary format.

        `method` is the HTTP method of the mocked endpoint

        `url` is the url or url pattern of the mocked endpoint, e.g. /api or /api.*

        `url_match_type` is the wiremock url match pattern to use. Applicable values
        are:
        - `url` (match url and query params)
        - `urlPattern` (match url and query params with regex)
        - `urlPath` (match url)
        - `urlPathPattern` (match url with regex)

        `query_parameters` is a dictionary of query parameters to match

        `headers` is a dictionary containing headers to match (case-insensitive matching)

        `cookies` is a dictionary containing cookies to match

        `json_body` is a dictionary of the json attribute(s) to match

        `regex_matching` is a boolean value which, if enabled, uses regex to match
        query parameter and header values
        """
        req = {}
        req['method'] = method
        req[url_match_type] = url

        match_type = 'matches' if regex_matching else 'equalTo'

        if query_parameters:
            req['queryParameters'] = {key: {match_type: value}
                                      for (key, value) in query_parameters.items()}

        if headers:
            req['headers'] = {key: {match_type: value, 'caseInsensitive': True}
                              for (key, value) in headers.items()}

        if cookies:
            req['cookies'] = {key: {match_type: value}
                              for (key, value) in cookies.items()}

        if json_body:
            req['bodyPatterns'] = [{'equalToJson': json.dumps(json_body),
                                    'ignoreArrayOrder': True,
                                    'ignoreExtraElements': True}]

        return req

    def create_mock_response(self, status, status_message=None,
                             headers=None, json_body=None, template=False):
        """Creates a mock response to be used by wiremock.

        Returns the response in a dictionary format.

        `status` is the HTTP status code of the response

        `status_message` is the HTTP status message of the response

        `headers` is a dictionary of headers to be added to the response

        `json_body` is a dictonary of JSON attribute(s) to be added to the response body

        `template` is a boolean value which specifies whether to use templating in the response,
        e.g. for copying a parameter, header or body value from the request to the response
        """
        rsp = {}
        rsp['status'] = int(status)
        rsp['headers'] = headers

        if status_message:
            rsp['statusMessage'] = status_message

        if json_body:
            rsp['jsonBody'] = json_body

        if template:
            rsp['transformers'] = ['response-template']

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

    def create_default_mock_mapping(self, method, url, status=200, status_message=None,
                                    response_headers=None, response_body=None, template=False):
        """Creates a default expectation to be used by wiremock.

        `method` is the HTTP method of the mocked endpoint

        `url` is the url pattern of the mocked endpoint(s), e.g. /.*api.*

        `status` is the HTTP status code of the response

        `status_message` is the HTTP status message of the response

        `response_headers` is a dictionary of headers to be added to the response

        `response_body` is a dictonary of JSON attribute(s) to be added to the response body

        `template` is a boolean value which specifies whether to use templating in the response,
        e.g. for copying a parameter, header or body value from the request to the response
        """
        req = self.create_mock_request_matcher(method, url, url_match_type='urlPathPattern')
        rsp = self.create_mock_response(status, status_message,
                                        response_headers, response_body, template)
        self.create_mock_mapping(req, rsp)

    def create_mock_mapping_with_data(self, data):
        """Creates a mapping with defined data to be used by wiremock.

        `data` is a dictionary or JSON string with mapping data. Please see
        [http://wiremock.org/docs/api/|WireMock documentation] for the detailed API reference.
        """
        self._send_request("/__admin/mappings", data)

    def get_requests(self, url, method=None):
        """Returns an array containing all requests received by wiremock for a given url pattern.

        `url` is the url pattern of the endpoint(s), e.g. /.*api.*

        `method` is the HTTP method of the requests
        """
        data = {}

        if method:
            data['method'] = method

        data['urlPathPattern'] = url
        rsp = self._send_request("/__admin/requests/find", data)
        return rsp.json()['requests']

    def get_previous_request(self, url, method=None):
        """Returns the last request received by wiremock for a given url pattern.

        `url` is the url pattern of the endpoint(s), e.g. /.*api.*

        `method` is the HTTP method of the request
        """
        return self.get_requests(url, method)[-1]

    def get_previous_request_body(self, url, method=None):
        """Returns the body of the last request received by wiremock for a given url pattern
        in dictionary form.

        `url` is the url pattern of the endpoint(s), e.g. /.*api.*

        `method` is the HTTP method of the request
        """
        body = self.get_requests(url, method)[-1]['body']
        return json.loads(body)

    def reset_mock_mappings(self):
        """Resets all mock mappings on the wiremock server.
        """
        self._send_request("/__admin/mappings/reset")

    def reset_request_log(self):
        """Resets all logged requests on the wiremock server.
        """
        self._send_request("/__admin/requests/reset")

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

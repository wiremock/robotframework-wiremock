import requests
import json
from urllib.parse import urljoin
from robot.api import logger

from version import VERSION

__version__ = VERSION


class WireMockLibrary(object):

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__

    def create_mock_session(self, base_url):
        """Create an HTTP session towards wiremock"""
        logger.debug("robotframework-wiremock libary version: {}".format(__version__))

        self.base_url = base_url
        self.session = requests.Session()

    def create_mock_request_matcher(self, method, url, json_body=None):
        """Create a mock response to be used by wiremock"""
        req = {}
        req['method'] = method
        req['url'] = url

        if json_body:
            req['bodyPatterns'] = [{'equalToJson': json.dumps(json_body),
                                    'ignoreArrayOrder': True,
                                    'ignoreExtraElements': True}]

        return req

    def create_mock_response(self, status, headers=None, json_body=None):
        """Create a mock response to be used by wiremock"""
        rsp = {}
        rsp['status'] = int(status)
        rsp['headers'] = headers

        if json_body:
            rsp['jsonBody'] = json_body

        return rsp

    def create_mock_mapping(self, request, response):
        """Create an mapping to be used by wiremock"""
        data = {}
        data['request'] = request
        data['response'] = response

        self.create_mock_mapping_with_data(data)

    def create_default_mock_mapping(self, method, url, status=200,
                                    response_headers=None, response_body=None):
        """Create a default expectation to be used by wiremock"""
        req = self.create_mock_request_matcher(method, url)
        rsp = self.create_mock_response(status, response_headers, response_body)
        self.create_mock_mapping(req, rsp)

    def create_mock_mapping_with_data(self, data):
        """Create an mapping with defined data to be used by wiremock"""
        self._send_request("/__admin/mappings", data)

    def reset_mock_mappings(self):
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

# coding: utf-8

import json

from wtforms.validators import ValidationError

from prettyconf import config

import requests

from echod.forms import MockForm
from echod.utils import url_path_join

request_headers = {
    'content_type': 'application/json',
    'accept': 'application/json',
}


class Mock(object):
    def __init__(self, expectation, host=None, port=None, docker=False):
        form = MockForm(data=expectation)
        if not form.validate():
            raise ValidationError(form.errors)

        self.expectation = expectation

        self.host = host or config('ECHOD_API_HOST', default='127.0.0.1')
        self.port = port or config('ECHOD_API_PORT', default=9876)

        self.base_url = 'http://{}:{}'.format(self.host, self.port)
        self._session = requests.Session()

        self._urls = {
            'health': url_path_join(self.base_url, 'health', '/'),
            'mocks': url_path_join(self.base_url, 'mocks', '/'),
            'response': None,
        }
        self.mock_url = None

    def __enter__(self):
        response = self._session.request(method='PUT', url=self._urls['mocks'],
                                         headers=request_headers,
                                         data=json.dumps(self.expectation),
                                         timeout=1)

        if response.status_code != 201:
            raise Exception('Erro creating mock.')

        self.mock_url = url_path_join(self.base_url, response.json()['path'], '/')
        self._urls['response'] = self.mock_url

        return self

    def __exit__(self, exec_type, exc, tb):
        # Clean up
        pass

    def health(self):
        return self._session.request(method='GET', url=self._urls['health'])

    def response(self):
        body = ''
        headers = {}
        method = self.expectation['method'].lower()

        if 'request' in self.expectation:
            headers = self.expectation['request']['headers']
            body = self.expectation['request']['body']

        return self._session.request(method=method, url=self._urls['response'],
                                     headers=headers, data=json.dumps(body))

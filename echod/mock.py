# coding: utf-8

import json
import asyncio


from wtforms.validators import ValidationError

from prettyconf import config

import aiohttp

from echod import api
from echod.forms import MockForm

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

        self.loop = asyncio.get_event_loop()
        self.host = host or config('ECHOD_API_HOST', default='127.0.0.1')
        self.port = port or config('ECHOD_API_PORT', default=9876)

        self.server_url = None
        self.address = (self.host, self.port)

    async def __aenter__(self):
        # Start API
        self.handler, self.redis_pool = self.loop.run_until_complete(
            api.start(self.loop, self.host, self.port))

        # Configure the mock
        self.server_url = 'http://{}:{}/mocks/'.format(*self.address)
        response = await aiohttp.request('PUT', self.server_url,
                                         headers=request_headers,
                                         data=json.dumps(self.expectation))
        if response.status_code != 201:
            raise Exception('Erro creating mock.')
        self.mock_path = response.json()['path']
        return self

    async def __aexit__(self, exec_type, exc, tb):
        # Clean up
        self.loop.run_until_complete(self.handler.finish_connections(1.0))
        self.loop.run_until_complete(self.redis_pool.clear())
        api.stop(self.loop)
        self.loop.close()

    async def health(self):
        health_url = 'http://{}:{}/health/'.format(*self.address)
        response = await aiohttp.request('GET', health_url)
        return response

    """
    async def response(self):
        body = ''
        headers = {}
        method = self.expectation['method'].lower()

        if 'request' in self.expectation:
            headers = self.expectation['request']['headers']
            body = self.expectation['request']['body']

        return await aiohttp.request(method, self.mock_path,
                                     headers=headers,
                                     data=json.dumps(body))
    """

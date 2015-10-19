# coding: utf-8
import json
from urllib.parse import urlsplit, splitport

import pytest

import aiohttp

from echod.mock import Mock

request_headers = {
    'content_type': 'application/json',
    'accept': 'application/json',
}


@pytest.mark.asyncio
def test_mock_client(api_server):
    expectation = {
        'method': 'POST',
        'request': {'body': {'email': 'john@doe.com',
                             'name': 'John Doe',
                             'password': 'secret'},
                    'headers': {'accept': 'application/json',
                                'content_type': 'application/json'}},
        'response': {'body': {'email': 'john@doe.com', 'name': 'John Doe'},
                     'headers': {'content_type': 'application/json'},
                     'status_code': 201}
    }

    netloc = urlsplit(api_server).netloc
    host, port = splitport(netloc)

    with Mock(expectation) as client:
        health = client.health()
        response = client.response()

        assert health.status_code == 200
        assert response.status_code == 201

        data = json.dumps(expectation['request']['body'])
        response = yield from aiohttp.request('POST', client.mock_url,
                                              data=data,
                                              headers=request_headers)
        assert response.status == 201


@pytest.mark.asyncio
def test_mock_client_without_request(api_server):
    expectation = {
        'method': 'POST',
        'response': {'body': {'email': 'john@doe.com', 'name': 'John Doe'},
                     'headers': {'content_type': 'application/json'},
                     'status_code': 201}
    }

    netloc = urlsplit(api_server).netloc
    host, port = splitport(netloc)

    with Mock(expectation) as client:
        health = client.health()
        response = client.response()

        assert health.status_code == 200
        assert response.status_code == 201

        data = json.dumps('')
        response = yield from aiohttp.request('POST', client.mock_url,
                                              data=data,
                                              headers=request_headers)
        assert response.status == 201

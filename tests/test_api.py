# coding: utf-8

import json
from urllib.parse import urljoin

import aiohttp

import pytest


content_type = 'application/json; charset=utf-8'

payload = {
    'name': 'Joaozinho',
    'age': 9,
}

str_payload = {
    'name': 'Joaozinho',
    'age': '9',
}

DEFAULT_HEADER = {
    'Content-Length': '31',
    'Content-Type': '',
    'Host': 'localhost'
}

ZERO_LENGTH_HEADER = {
    'Content-Length': '0',
    'Content-Type': '',
    'Host': 'localhost'
}


# Mock tests


@pytest.mark.asyncio
def test_get_mock(api_server):
    url = urljoin(api_server, '/mocks/')
    response = yield from aiohttp.request('GET', url)

    assert response.status == 200
    assert response.reason == 'OK'
    assert response.headers['content-type'] == content_type
    response_json = yield from response.json()
    assert response_json == {'mocks': {}}


@pytest.mark.asyncio
def test_put_mock(api_server):
    response_must_contain = {
        'status_code': 201,
        'body': {
            'name': 'John Doe',
            'email': 'john@doe.com',
        },
        'headers': {
            'content_type': 'application/json',
        },
    }

    request_headers = {
        'content_type': 'application/json',
        'accept': 'application/json',
    }

    request_must_contain = {
        'body': {
            'name': 'John Doe',
            'email': 'john@doe.com',
            'password': 'secret',
        },
        'headers': request_headers,
    }

    expectation = {
        'method': 'POST',
        'path': '/v1/users/',
        'request': request_must_contain,
        'response': response_must_contain,
    }

    url = urljoin(api_server, '/mocks/')

    # Configure the mock
    response = yield from aiohttp.request('PUT', url,
                                          data=json.dumps(expectation),
                                          headers=request_headers)

    assert response.status == 201
    assert response.reason == 'Created'
    assert response.headers['content-type'] == content_type
    response_json = yield from response.json()
    assert 'path' in response_json.keys()

    # Use the mock
    post_url = urljoin(api_server, response_json['path'])
    post_body = json.dumps(request_must_contain['body'])
    response = yield from aiohttp.request('POST', post_url,
                                          data=post_body,
                                          headers=request_headers)

    assert response.status == 201
    assert response.reason == 'Created'
    assert response.headers['content-type'] == content_type
    response_json = yield from response.json()
    assert 'email' in response_json.keys()
    assert 'name' in response_json.keys()


# Health


@pytest.mark.asyncio
def test_health(api_server):
    url = urljoin(api_server, '/health/')
    response = yield from aiohttp.request('GET', url)

    assert response.status == 200
    assert response.reason == 'OK'
    assert response.headers['content-type'] == content_type
    response_json = yield from response.json()
    assert response_json == {'status': 'ok'}


# Callback tests


@pytest.mark.asyncio
def test_queue_request_return_status_200(api_server):
    response = yield from aiohttp.request('POST',
                                          urljoin(api_server, '/callbacks/app/queue/'),
                                          data=json.dumps(payload))

    assert response.status == 200


@pytest.mark.asyncio
def test_queue_request_return_json(api_server):
    response = yield from aiohttp.request('POST',
                                          urljoin(api_server, '/callbacks/app/queue/'),
                                          data=json.dumps(payload))

    response_json = yield from response.json()
    assert response_json['request']['method'] == 'POST'
    assert response_json['request']['data'] == payload

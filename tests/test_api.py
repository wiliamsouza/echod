# coding: utf-8

import json
from urllib.parse import urljoin

import requests


def test_get_mock_handler():
    response = requests.get('http://127.0.0.1:8080/mocks/')

    assert response.status_code == 200
    assert response.reason == 'OK'
    assert response.headers['content-type'] == 'application/json; charset=utf-8'
    assert response.json() == {'mocks': []}


def test_put_mock_handler():
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

    base_url = 'http://127.0.0.1:8080/'

    # Configure the mock
    response = requests.put(urljoin(base_url, '/mocks/'),
                            json.dumps(expectation),
                            headers=request_headers)

    assert response.status_code == 201
    assert response.reason == 'Created'
    assert response.headers['content-type'] == 'application/json; charset=utf-8'
    assert 'path' in response.json().keys()

    # Use the mock
    response = requests.post(urljoin(base_url, response.json()['path']),
                             json.dumps(request_must_contain['body']),
                             headers=request_headers)

    assert response.status_code == 201
    assert response.reason == 'Created'
    assert response.headers['content-type'] == 'application/json; charset=utf-8'
    assert 'email' in response.json().keys()
    assert 'name' in response.json().keys()

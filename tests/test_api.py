# coding: utf-8

import json
from urllib.parse import urljoin

import aiohttp

import pytest

from echod.utils import decode_json


content_type = 'application/json; charset=utf-8'

payload = {
    'name': 'Joaozinho',
    'age': 9,
}

str_payload = {
    'name': 'Joaozinho',
    'age': '9',
}

json_payload = json.dumps(payload)

default_header = {
    'Content-Length': '31',
    'Content-Type': '',
    'Host': 'localhost'
}

zero_length_header = {
    'Content-Length': '0',
    'Content-Type': '',
    'Host': 'localhost'
}

request_headers = {
    'content_type': 'application/json',
    'accept': 'application/json',
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
    expectation = {
        'method': 'POST',
        'path': '/v1/users/',
        'request': {'body': {'email': 'john@doe.com',
                             'name': 'John Doe',
                             'password': 'secret'},
                    'headers': {'accept': 'application/json',
                                'content_type': 'application/json'}},
        'response': {'body': {'email': 'john@doe.com', 'name': 'John Doe'},
                     'headers': {'content_type': 'application/json'},
                     'status_code': 201}
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
    post_body = json.dumps(expectation['request']['body'])
    response = yield from aiohttp.request('POST', post_url,
                                          data=post_body,
                                          headers=request_headers)

    assert response.status == 201
    assert response.reason == 'Created'
    assert response.headers['content-type'] == content_type
    response_json = yield from response.json()
    assert 'email' in response_json.keys()
    assert 'name' in response_json.keys()


@pytest.mark.asyncio
def test_put_mock_without_request_expectation(api_server):
    expectation = {
        'method': 'PUT',
        'path': '/v1/users/',
        'response': {'body': {'email': 'john@doe.com', 'name': 'John Doe'},
                     'headers': {'content_type': 'application/json'},
                     'status_code': 200}
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
    put_url = urljoin(api_server, response_json['path'])
    put_body = json.dumps({})
    response = yield from aiohttp.request('PUT', put_url,
                                          data=put_body,
                                          headers=request_headers)

    assert response.status == 200
    assert response.reason == 'OK'
    assert response.headers['content-type'] == content_type
    response_json = yield from response.json()
    assert 'email' in response_json.keys()
    assert 'name' in response_json.keys()


@pytest.mark.asyncio
def test_method_not_allowed(api_server):
    expectation = {
        'method': 'GET',
        'path': '/v1/users/',
        'response': {'body': {'email': 'john@doe.com', 'name': 'John Doe'},
                     'headers': {'content_type': 'application/json'},
                     'status_code': 200}
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
    put_url = urljoin(api_server, response_json['path'])
    response = yield from aiohttp.request('PUT', put_url)

    assert response.status == 405
    assert response.reason == 'Method Not Allowed'


@pytest.mark.asyncio
def test_not_found(api_server):
    post_url = urljoin(api_server, '/mock/noexist/url/')
    post_body = '{}'
    response = yield from aiohttp.request('POST', post_url,
                                          data=post_body,
                                          headers=request_headers)
    assert response.status == 404
    assert response.reason == 'Not Found'


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
    url = urljoin(api_server, '/callbacks/app/queue/')
    response = yield from aiohttp.request('POST',
                                          url,
                                          data=json_payload)

    assert response.status == 200


@pytest.mark.asyncio
def test_queue_request_return_json(api_server):
    url = urljoin(api_server, '/callbacks/app/queue/')
    response = yield from aiohttp.request('POST', url,
                                          data=json_payload)

    response_json = yield from response.json()
    assert response_json['request']['method'] == 'POST'
    assert response_json['request']['data'] == payload


@pytest.mark.asyncio
def test_queue_request_store_request(api_server, redis):
    url = urljoin(api_server, '/callbacks/app/queue/')
    yield from aiohttp.request('POST', url, data=json_payload)

    assert redis.llen('app-queue') == 1


@pytest.mark.asyncio
def test_queue_request_store_json(api_server, redis):
    url = urljoin(api_server, '/callbacks/app/queue/')
    yield from aiohttp.request('POST', url, data=json_payload,
                               headers={'X-Region': 'Sao_Paulo'})

    db_json = decode_json(redis.rpop('app-queue').decode('utf-8'))

    assert db_json['header']['X-REGION'] == 'Sao_Paulo'
    assert db_json['method'] == 'POST'
    assert db_json['data'] == payload


"""
@pytest.mark.asyncio
def test_queue_request_with_additional_url_return_status_200(api_server):
    url = '/callbacks/app/queue/some/more/url/here'
    response = yield from aiohttp.request('POST', url,
                                          data=json_payload)

    assert response.status == 200


@pytest.mark.asyncio
def test_queue_request_with_additional_url_json(api_server, redis):
    url = '/callbacks/app/queue/some/more/url/here'
    yield from aiohttp.request('POST', url,
                               data=json_payload)

    expected_data = {
        'method': 'POST',
        'data': payload,
        'additional_url': 'some/more/url/here',
        'header': default_header,
    }
    assert decode_json(redis.rpop('app-queue')) == expected_data
"""


@pytest.mark.asyncio
def test_queue_request_store_multiple_requests(api_server, redis):
    url = urljoin(api_server, '/callbacks/app/queue/')
    yield from aiohttp.request('POST', url, data=json_payload)
    yield from aiohttp.request('POST', url, data=json_payload)
    yield from aiohttp.request('POST', url, data=json_payload)

    assert redis.llen('app-queue') == 3


@pytest.mark.asyncio
def test_queue_request_store_request_different_apps(api_server, redis):
    url1 = urljoin(api_server, '/callbacks/app1/queue/')
    url2 = urljoin(api_server, '/callbacks/app2/queue/')
    yield from aiohttp.request('POST', url1, data=json_payload)
    yield from aiohttp.request('POST', url2, data=json_payload)

    assert redis.llen('app1-queue') == 1
    assert redis.llen('app2-queue') == 1


@pytest.mark.asyncio
def test_queue_request_store_request_different_queues(api_server, redis):
    url1 = urljoin(api_server, '/callbacks/app/queue1/')
    url2 = urljoin(api_server, '/callbacks/app/queue2/')
    yield from aiohttp.request('POST', url1, data=json_payload)
    yield from aiohttp.request('POST', url2, data=json_payload)

    assert redis.llen('app-queue1') == 1
    assert redis.llen('app-queue2') == 1


@pytest.mark.asyncio
def test_get_requests_return_status_200(api_server):
    url = urljoin(api_server, '/callbacks/_all/app/queue/')
    response = yield from aiohttp.request('GET', url)
    assert response.status == 200


@pytest.mark.asyncio
def test_get_requests_empty(api_server):
    url = urljoin(api_server, '/callbacks/_all/app/queue/')
    response = yield from aiohttp.request('GET', url)
    response_json = yield from response.json()
    assert response_json == {'requests': []}


@pytest.mark.asyncio
def test_get_requests_one_request(api_server):
    url = urljoin(api_server, '/callbacks/app/queue/')
    yield from aiohttp.request('POST', url, data=json_payload)

    url_all = urljoin(api_server, '/callbacks/_all/app/queue/')
    response = yield from aiohttp.request('GET', url_all)

    response_json = yield from response.json()

    assert response_json['requests'][0]['method'] == 'POST'
    assert response_json['requests'][0]['data'] == payload


# TODO: Make it work
"""
@pytest.mark.asyncio
def test_get_requests_multiple_request(api_server):
    url = urljoin(api_server, '/callbacks/app/queue/')
    yield from aiohttp.request('POST', url, data=json_payload)
    yield from aiohttp.request('PUT', url, data=json_payload)
    yield from aiohttp.request('PATCH', url, data=json_payload)
    # TODO: Make it work
    # yield from aiohttp.request('GET', url, query_string=payload)
    yield from aiohttp.request('DELETE', url)

    url_all = urljoin(api_server, '/callbacks/_all/app/queue/')
    response = yield from aiohttp.request('GET', )

    expected_data = [
        {'method': 'POST', 'data': payload, 'header': default_header,
         'additional_url': ''},
        {'method': 'PUT', 'data': payload, 'header': default_header,
         'additional_url': ''},
        {'method': 'PATCH', 'data': payload, 'header': default_header,
         'additional_url': ''},
        {'method': 'GET', 'data': str_payload, 'header': zero_length_header,
         'additional_url': ''},
        {'method': 'DELETE', 'data': {}, 'header': zero_length_header,
         'additional_url': ''},
    ]

    response_json = yield from response.json()
    assert response_json == {'requests': expected_data}
"""


@pytest.mark.asyncio
def test_get_requests_remove_key(api_server, redis):
    url = urljoin(api_server, '/callbacks/app/queue/')
    url_all = urljoin(api_server, '/callbacks/_all/app/queue/')
    yield from aiohttp.request('POST', url, data=json_payload)
    yield from aiohttp.request('GET', url_all)

    assert not redis.exists('app-queue')


@pytest.mark.asyncio
def test_first_request_return_status_200(api_server):
    url = urljoin(api_server, '/callbacks/_first/app/queue/')
    response = yield from aiohttp.request('GET', url)
    assert response.status == 200


@pytest.mark.asyncio
def test_first_request_empty(api_server):
    url = urljoin(api_server, '/callbacks/_first/app/queue/')
    response = yield from aiohttp.request('GET', url)

    response_json = yield from response.json()
    assert response_json == {'request': {}}


@pytest.mark.asyncio
def test_first_request_one_request(api_server):
    url = urljoin(api_server, '/callbacks/app/queue/')
    yield from aiohttp.request('POST', url, data=json_payload)

    url_first = urljoin(api_server, '/callbacks/_first/app/queue/')
    response = yield from aiohttp.request('GET', url_first)
    response_json = yield from response.json()

    assert response_json['request']['method'] == 'POST'
    assert response_json['request']['data'] == payload


@pytest.mark.asyncio
def test_first_request_multiple_request(api_server):
    url = urljoin(api_server, '/callbacks/app/queue/')
    yield from aiohttp.request('POST', url, data=json_payload)
    yield from aiohttp.request('PUT', url, data=json_payload)
    yield from aiohttp.request('PATCH', url, data=json_payload)
    # yield from aiohttp.request('GET', url, query_string=payload)
    yield from aiohttp.request('DELETE', url)

    url_first = urljoin(api_server, '/callbacks/_first/app/queue/')
    response = yield from aiohttp.request('GET', url_first)
    response_json = yield from response.json()

    assert response_json['request']['method'] == 'POST'
    assert response_json['request']['data'] == payload


@pytest.mark.asyncio
def test_last_request_return_status_200(api_server):
    url = urljoin(api_server, '/callbacks/_last/app/queue/')
    response = yield from aiohttp.request('GET', url)
    assert response.status == 200


@pytest.mark.asyncio
def test_last_request_empty(api_server):
    url = urljoin(api_server, '/callbacks/_last/app/queue/')
    response = yield from aiohttp.request('GET', url)

    response_json = yield from response.json()
    assert response_json == {'request': {}}


@pytest.mark.asyncio
def test_last_request_one_request(api_server):
    url = urljoin(api_server, '/callbacks/app/queue/')
    yield from aiohttp.request('POST', url, data=json_payload)

    url_last = urljoin(api_server, '/callbacks/_last/app/queue/')
    response = yield from aiohttp.request('GET', url_last)

    response_json = yield from response.json()

    assert response_json['request']['method'] == 'POST'
    assert response_json['request']['data'] == payload


"""
@pytest.mark.asyncio
def test_last_request_multiple_request(api_server):
    yield from aiohttp.request('POST', urljoin(api_server, '/callbacks/app/que
    yield from aiohttp.request('PUT', urljoin(api_server, '/callbacks/app/queu
    yield from aiohttp.request('PATCH', urljoin(api_server, '/callbacks/app/qu
    yield from aiohttp.request('GET', urljoin(api_server, '/callbacks/app/queu
    yield from aiohttp.request('DELETE', urljoin(api_server, '/callbacks/app/q

    response = yield from aiohttp.request('GET', urljoin(api_server, '/callbac

    expected_data = {'method': 'DELETE', 'data': {}, 'additional_url': '', 'he

    assert decode_json(response.data) == {'request': expected_data}
"""


@pytest.mark.asyncio
def test_clean_requests_none_request(api_server, redis):
    url = urljoin(api_server, '/callbacks/_clean/app/queue/')
    yield from aiohttp.request('GET', url)
    assert not redis.exists('app-queue')


@pytest.mark.asyncio
def test_clean_requests_none_request_return_status_200(api_server):
    url = urljoin(api_server, '/callbacks/_clean/app/queue/')
    response = yield from aiohttp.request('GET', url)
    assert response.status == 200


@pytest.mark.asyncio
def test_clean_requests_none_request_return_empty_json(api_server):
    url = urljoin(api_server, '/callbacks/_clean/app/queue/')
    response = yield from aiohttp.request('GET', url)
    response_json = yield from response.json()

    assert response_json == {}


@pytest.mark.asyncio
def test_clean_requests_multiple_requests(api_server, redis):
    url = urljoin(api_server, '/callbacks/app/queue/')
    yield from aiohttp.request('POST', url, data=json_payload)
    yield from aiohttp.request('PUT', url, data=json_payload)
    yield from aiohttp.request('PATCH', url, data=json_payload)
    yield from aiohttp.request('DELETE', url)

    url_clean = urljoin(api_server, '/callbacks/_clean/app/queue/')
    yield from aiohttp.request('GET', url_clean)
    assert not redis.exists('app-queue')

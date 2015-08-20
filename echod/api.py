# coding: utf-8

import json
import uuid
import asyncio
import logging

import aioredis

from aiohttp import web

from prettyconf import config

from echod.utils import (encode_json, decode_json, generate_key,
                         normalize_path, request_to_dict, hash_dict,
                         compare_hash)

log = logging.getLogger(__name__)
app = None
redis_pool = None


@asyncio.coroutine
def get_mock(request):
    data = json.dumps({'mocks': request.app['mock_db']})
    return web.Response(text=data, content_type='application/json')


@asyncio.coroutine
def put_mock(request):
    data = yield from request.json()
    uuid_hex = uuid.uuid4().hex
    path = yield from normalize_path('/mock/{}/{}/'.format(uuid_hex,
                                                           data['path']))
    request.app.router.add_route(data['method'], path, mock)
    request.app['mock_db'][path] = data
    return web.Response(text=json.dumps({'path': path}),
                        status=201,
                        content_type='application/json')


@asyncio.coroutine
def get_proxy(request):
    data = json.dumps({'proxies': []})
    return web.Response(text=data, content_type='application/json')


@asyncio.coroutine
def put_proxy(request):
    return web.Response(text=json.dumps({'status': 'ok'}),
                        content_type='application/json')


@asyncio.coroutine
def all_callback(request):
    app = request.match_info['app']
    queue = request.match_info['queue']
    key = yield from generate_key(app, queue)

    with (yield from request.app['redis_pool']) as redis:
        requests = yield from redis.lrange(key, 0, -1)
        requests = [decode_json(r) for r in requests]
        redis.delete(key)

    data = json.dumps({'requests': requests})
    return web.Response(text=data, content_type='application/json')


@asyncio.coroutine
def first_callback(request):
    app = request.match_info['app']
    queue = request.match_info['queue']
    key = yield from generate_key(app, queue)

    with (yield from request.app['redis_pool']) as redis:
        request_ = yield from redis.lpop(key)
        request_ = decode_json(request_)

    data = json.dumps({'request': request_})
    return web.Response(text=data, content_type='application/json')


@asyncio.coroutine
def last_callback(request):
    app = request.match_info['app']
    queue = request.match_info['queue']
    key = yield from generate_key(app, queue)

    with (yield from request.app['redis_pool']) as redis:
        request_ = yield from redis.rpop(key)
        request_ = decode_json(request_)

    data = json.dumps({'request': request_})
    return web.Response(text=data, content_type='application/json')


@asyncio.coroutine
def clean_callback(request):
    app = request.match_info['app']
    queue = request.match_info['queue']
    key = yield from generate_key(app, queue)

    with (yield from request.app['redis_pool']) as redis:
        redis.delete(key)

    return web.Response(text=json.dumps({}),
                        content_type='application/json')


@asyncio.coroutine
def callback(request):
    # TODO: Add support for addtional_url

    app = request.match_info['app']
    queue = request.match_info['queue']
    key = yield from generate_key(app, queue)

    request_ = yield from request_to_dict(request)
    json_ = yield from encode_json(request_)
    with (yield from request.app['redis_pool']) as redis:
        redis.rpush(key, json_)

    return web.Response(text=json.dumps({'request': request_}),
                        content_type='application/json')


@asyncio.coroutine
def mock(request):
    received = yield from request.json()
    # Check/Validate for KeyError
    config = request.app['mock_db'][request.path]
    response = config['response']['body']
    expected = config['request']['body']
    status = config['response']['status_code']
    content_type = config['response']['headers']['content_type']
    expected_hash = yield from hash_dict(expected)
    received_hash = yield from hash_dict(received)
    if not compare_hash(expected_hash, received_hash):
        status = 400
        response = {
            'message': 'Received request data did not match with expected',
            'received_data': received,
            'expected_data': expected,
        }
    return web.Response(text=json.dumps(response),
                        status=status,
                        content_type=content_type)


@asyncio.coroutine
def health(request):
    return web.Response(text=json.dumps({'status': 'ok'}),
                        content_type='application/json')


@asyncio.coroutine
def start(loop, api_host='127.0.0.1', api_port=9876):
    app = web.Application(loop=loop)
    app['mock_db'] = {}
    redis_address = (config('ECHO_REDIS_HOST', default='127.0.0.1'),
                     config('ECHO_REDIS_PORT', default=6379))
    redis_db = config('ECHO_REDIS_DB', default=0)
    redis_pool = yield from aioredis.create_pool(redis_address, db=redis_db,
                                                 minsize=5, maxsize=10,
                                                 encoding='utf-8', loop=loop)
    app['redis_pool'] = redis_pool

    # Mock
    app.router.add_route('GET', '/mocks/', get_mock)
    app.router.add_route('PUT', '/mocks/', put_mock)

    # Proxies
    app.router.add_route('GET', '/proxies/', get_proxy)
    app.router.add_route('PUT', '/proxies/', put_proxy)

    # Callbacks
    app.router.add_route('*', '/callbacks/{app}/{queue}/', callback)
    app.router.add_route('GET', '/callbacks/_all/{app}/{queue}/', all_callback)
    app.router.add_route('GET', '/callbacks/_first/{app}/{queue}/',
                         first_callback)
    app.router.add_route('GET', '/callbacks/_last/{app}/{queue}/',
                         last_callback)
    app.router.add_route('GET', '/callbacks/_clean/{app}/{queue}/',
                         clean_callback)

    # Health
    app.router.add_route('GET', '/health/', health)

    handler = app.make_handler()
    server = yield from loop.create_server(handler, api_host, api_port)
    address = server.sockets[0].getsockname()
    log.info('API started at http://{}:{}/'.format(*address))
    return server, handler, redis_pool


def stop(loop):
    if app:
        loop.run_until_complete(app.finish())

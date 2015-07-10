# coding: utf-8

import json
import uuid
import hashlib
import asyncio
import logging

from aiohttp import web


log = logging.getLogger(__name__)
app = None


# TODO: Move to a utils.py file
@asyncio.coroutine
def normalize_path(path):
    """ Normalize path

    Removes double slash from path
    """
    path = '/'.join([split for split in path.split('/') if split != ''])

    if not path.startswith('/'):
        path = '/{}'.format(path)

    if not path.endswith('/'):
        path = '{}/'.format(path)

    return path


# TODO: Move to a utils.py file
@asyncio.coroutine
def hash_dict(dictionary):
    json_data = json.dumps(dictionary, sort_keys=True).encode('utf-8')
    return hashlib.sha1(json_data).hexdigest()


# TODO: Move to a utils.py file
def compare_hash(expected_hash, received_hash):
    return expected_hash == received_hash


@asyncio.coroutine
def get_mock(request):
    data = json.dumps({'mocks': []})
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
def get_callback(request):
    data = json.dumps({'callbacks': []})
    return web.Response(text=data, content_type='application/json')


@asyncio.coroutine
def put_callback(request):
    return web.Response(text=json.dumps({'status': 'ok'}),
                        content_type='application/json')


@asyncio.coroutine
def callback(request):
    return web.Response(text=json.dumps({'status': 'ok'}),
                        content_type='application/json')


@asyncio.coroutine
def mock(request):
    received = yield from request.json()
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
def start(loop):
    app = web.Application(loop=loop)
    app['mock_db'] = {}
    app['callback_db'] = {}

    app.router.add_route('GET', '/mocks/', get_mock)
    app.router.add_route('PUT', '/mocks/', put_mock)
    app.router.add_route('GET', '/proxies/', get_proxy)
    app.router.add_route('PUT', '/proxies/', put_proxy)
    app.router.add_route('GET', '/callbacks/', get_callback)
    app.router.add_route('PUT', '/callbacks/', put_callback)
    app.router.add_route('*', '/callback/', callback)

    host = '127.0.0.1'
    port = 8080
    handler = app.make_handler()
    server = yield from loop.create_server(handler, host, port)
    name = server.sockets[0].getsockname()
    log.info('API started at http://{}:{}/'.format(*name))
    return server, handler


def stop(loop):
    if app:
        loop.run_until_complete(app.finish())

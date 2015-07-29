# coding: utf-8

import json
import hashlib
import asyncio


@asyncio.coroutine
def generate_key(app, queue):
    return '{}-{}'.format(app, queue)


@asyncio.coroutine
def request_to_dict(request_):
    try:
        data = yield from request_.json()
    except:
        data = yield from request_.text()

    header = dict(request_.headers)

    return {
        'method': request_.method,
        'header': header,
        'data': data,
    }


@asyncio.coroutine
def encode_json(data):
    return json.dumps(data).encode('latin-1')


def decode_json(data):
    if data:
        return json.loads(data.decode('latin-1'))
    else:
        return dict()


# TODO: Changes to use https://github.com/rbaier/python-urltools/
#       do not forget PUBLIC_SUFFIX_LIST env var!
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


@asyncio.coroutine
def hash_dict(dictionary):
    json_data = json.dumps(dictionary, sort_keys=True).encode('utf-8')
    return hashlib.sha1(json_data).hexdigest()


def compare_hash(expected_hash, received_hash):
    return expected_hash == received_hash

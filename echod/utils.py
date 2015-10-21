# coding: utf-8

import json
import hashlib
import asyncio
from urllib.parse import urlsplit, urlunsplit


@asyncio.coroutine
def generate_key(app, queue):
    return '{}-{}'.format(app, queue)


@asyncio.coroutine
def request_to_dict(request):
    try:
        data = yield from request.json()
    except:
        data = yield from request.text()

    header = dict(request.headers)

    return {
        'method': request.method,
        'header': header,
        'data': data,
    }


@asyncio.coroutine
def encode_json(data):
    return json.dumps(data)


def decode_json(data):
    if data:
        return json.loads(data)
    else:
        return dict()


# TODO: Changes to use https://github.com/rbaier/python-urltools/
#       do not forget PUBLIC_SUFFIX_LIST env var!
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


def url_path_join(*parts):
    def first_of_each(*sequences):
        return (next((x for x in sequence if x), '') for sequence in sequences)
    schemes, netlocs, paths, queries, fragments = zip(*(urlsplit(part) for part in parts))
    scheme, netloc, query, fragment = first_of_each(schemes, netlocs, queries,
                                                    fragments)
    path = '/'.join(x.strip('/') for x in paths if x)
    return urlunsplit((scheme, netloc, path, query, fragment))

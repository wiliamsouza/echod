# coding: utf-8

import pytest

from echod import api


@pytest.yield_fixture(autouse=True)
def redis():
    """ Redis

    We uses a normal(not asyncio) version of redis lib here because of some
    issues using asyncio version and yield fixtures.
    """
    import redis

    redis = redis.StrictRedis(host='127.0.0.1', port=6379)
    yield redis
    redis.flushdb()


@pytest.yield_fixture()
def api_server(event_loop, unused_tcp_port):
    api_port = unused_tcp_port
    server, handler, redis_pool = event_loop.run_until_complete(
        api.start(event_loop, api_port=api_port))

    yield 'http://127.0.0.1:{}/'.format(api_port)
    event_loop.run_until_complete(handler.finish_connections(1.0))
    event_loop.run_until_complete(redis_pool.clear())
    api.stop(event_loop)

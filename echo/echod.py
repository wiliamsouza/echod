#!/bin/env python3
# coding: utf-8

import sys
import asyncio
import logging

from prettyconf import config

from echo import api


debug = config("DEBUG", default=False, cast=config.boolean)
log = logging.getLogger('echo')
loga = logging.getLogger('asyncio')
if debug:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter('[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] ')
    log.addHandler(handler)
    log.setLevel(logging.DEBUG)
    loga.addHandler(logging.StreamHandler(sys.stdout))
    loga.setLevel(logging.DEBUG)


def main():
    loop = asyncio.get_event_loop()
    api_host = config('ECHO_API_HOST', default='127.0.0.1')
    api_port = config('ECHO_API_PORT', default=9876)
    server, handler, redis_pool = loop.run_until_complete(
        api.start(loop, api_host, api_port))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(handler.finish_connections(1.0))
        loop.run_until_complete(redis_pool.clear())
        api.stop(loop)

    loop.close()
    sys.exit(0)


if __name__ == '__main__':
    main()

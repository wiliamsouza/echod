#!/bin/env python3
# coding: utf-8

import sys
import asyncio
import logging

from echo import api


log = logging.getLogger('echo')
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    tcp_port = 8080
    server, handler, redis_pool = loop.run_until_complete(
        api.start(loop, tcp_port))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(handler.finish_connections(1.0))
        loop.run_until_complete(redis_pool.clear())
        api.stop(loop)

    loop.close()

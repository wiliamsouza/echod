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
    server, handler = loop.run_until_complete(api.start(loop))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(handler.finish_connections(1.0))
        api.stop(loop)

    loop.close()

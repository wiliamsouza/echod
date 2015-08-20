# coding: utf-8

import logging
import asyncio

log = logging.getLogger('echo')


class HTTPProxy(asyncio.Protocol):

    def __init__(self, backend):
        self.backend = backend
        self.host, self.port = backend.rsplit(':', 1)

    def connection_made(self, transport):
        log.debug('Connection made')
        self.transport = transport
        self.reader, self.writer = yield from asyncio.open_connection(
            self.host, self.port)
        log.info('connected to remote {}'.format(self.backend))

    def connection_lost(self, exc):
        log.debug('Connection lost')

    def data_received(self, data):
        log.debug('Data received')

    def eof_received(self):
        log.debug('Eof received')

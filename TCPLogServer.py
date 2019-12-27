# -*- coding: utf-8 -*-
import _pickle
import logging
import struct
from socketserver import StreamRequestHandler, ThreadingTCPServer

from config import *
from utils.EsHelper import EsHelper
from utils.GeoIpHelper import GeoIpHelper
from utils.RequestParser import RequestParser


class SocketLogHandler(StreamRequestHandler):
    def handle(self):
        print("connect from:", self.client_address)

        while True:
            chunk = self.request.recv(4)
            if len(chunk) < 4:
                break

            slen = struct.unpack(">L", chunk)[0]
            chunk = self.request.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.request.recv(slen - len(chunk))

            obj = _pickle.loads(chunk)
            record = logging.makeLogRecord(obj)
            message = record.getMessage()

            payload = RequestParser().tcp_access_log(message)
            payload['pot_ip'] = self.client_address[0]

            if TCP_LOG_PROXY_GEOIP_PATH:
                try:
                    payload['client_geoip'] = GeoIpHelper(TCP_LOG_PROXY_GEOIP_PATH).get(payload['client_ip'])
                except Exception as e:
                    print('Cannot get GeoIP {} {}'.format(payload['client_ip'], e))
            EsHelper(TCP_LOG_PROXY_ES_HOST, TCP_LOG_PROXY_ES_PORT, TCP_LOG_PROXY_ES_INDEX).send(payload)
        self.request.close()


if __name__ == '__main__':
    server = ThreadingTCPServer((TCP_LOG_PROXY_HOST, TCP_LOG_PROXY_PORT), SocketLogHandler)
    print('listening:', server.socket.getsockname())
    server.serve_forever()

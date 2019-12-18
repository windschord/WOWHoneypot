# -*- coding: utf-8 -*-
import base64
import json
import logging
import re
import ssl
import struct
import urllib
import urllib.request
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler

import cgi
from socketserver import StreamRequestHandler, ThreadingTCPServer
from urllib.parse import urlparse
import _pickle as cPickle

SERVER_HOST = 'localhost'
SERVER_PORT = 8888
ES_HOST = 'localhost'
ES_PORT = 9200
ES_INDEX = 'wowhoneypot'
ES_TYPE = 'wowhoneypot'


class SocketLogHandler(StreamRequestHandler):
    def handle(self):
        print("connect from:", self.client_address)
        alldata = ""
        while True:
            chunk = self.request.recv(4)
            if len(chunk) < 4:
                break

            slen = struct.unpack(">L", chunk)[0]
            chunk = self.request.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.request.recv(slen - len(chunk))

            obj = cPickle.loads(chunk)
            record = logging.makeLogRecord(obj)
            message = record.getMessage()
            print(message)
            message_ret = list(re.match('\[(.+)\] (.+) (.+) \"(.+) (.+) (.+)\" (\d+) (.+) (.+)$', message).groups())
            message_ret[0] = datetime.strptime(message_ret[0], "%Y-%m-%d %H:%M:%S%z"
                                               ).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            message_label = ['@timestamp', 'client_ip', 'hostname', 'method', 'path', 'version', 'status_code',
                             'match_result', 'request_all']

            payload = dict(zip(message_label, message_ret))
            payload['pot_ip'] = self.client_address[0]
            print(payload)
            self.post_to_es(payload)
        self.request.close()

    def post_to_es(self, payload):
        json_data = json.dumps(payload).encode("utf-8")
        invoke_url = "http://{host}:{port}/{index}/{type}".format(host=ES_HOST, port=ES_PORT,
                                                                  index=ES_INDEX, type=ES_TYPE)

        req = urllib.request.Request(invoke_url, data=json_data, method="POST",
                                     headers={'Content-type': 'application/json'})
        try:
            with urllib.request.urlopen(req) as response:
                the_page = response.read().decode("utf-8")
                print('res body: {}'.format(the_page))
        except Exception as e:
            print(e)


if __name__ == '__main__':
    server = ThreadingTCPServer((SERVER_HOST, SERVER_PORT), SocketLogHandler)
    print('listening:', server.socket.getsockname())
    server.serve_forever()

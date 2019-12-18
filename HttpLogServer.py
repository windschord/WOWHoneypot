# -*- coding: utf-8 -*-
import base64
import json
import re
import ssl
import urllib
import urllib.request
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler

import cgi
from urllib.parse import urlparse

SERVER_HOST = 'localhost'
SERVER_PORT = 8888
SERVER_KEY_FILE = 'cert/server.key'
SERVER_CERT_FILE = 'cert/server.crt'
ES_HOST = 'localhost'
ES_PORT = 9200
ES_INDEX = 'wowhoneypot'
ES_TYPE = 'wowhoneypot'


class PostHandler(BaseHTTPRequestHandler):
    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header(
            'WWW-Authenticate', 'Basic realm="Demo Realm"')
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        key = self.server.get_auth_key()
        ''' Present frontpage with user authentication. '''
        if self.headers.get('Authorization') == None:
            self.do_AUTHHEAD()

            response = {
                'success': False,
                'error': 'No auth header received'
            }

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))

        elif self.headers.get('Authorization') == 'Basic ' + str(key):
            self._parse_POST()
        else:
            self.do_AUTHHEAD()

            response = {
                'success': False,
                'error': 'Invalid credentials'
            }

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))


    def _parse_POST(self):
        # POST されたフォームデータを解析する
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     })
        # レスポンス開始
        self.send_response(200)
        self.end_headers()
        pot_ip = self.client_address[0]
        print(pot_ip)
        # フォームに POST されたデータを表示する
        if 'message' in form.keys():
            message = form['message'].value
        if not message and 'msg' in form.keys():
            message = form['msg'].value
        print(message)
        message_ret = list(re.match('\[(.+)\] (.+) (.+) \"(.+) (.+) (.+)\" (\d+) (.+) (.+)$', message).groups())
        message_ret[0] = datetime.strptime(message_ret[0], "%Y-%m-%d %H:%M:%S%z"
                                               ).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        message_label = ['@timestamp', 'client_ip', 'hostname', 'method', 'path', 'version', 'status_code',
                         'match_result', 'request_all']

        payload = dict(zip(message_label, message_ret))
        payload['pot_ip'] = pot_ip
        print(payload)
        self.post_to_es(payload)

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


class CustomHTTPServer(HTTPServer):
    key = ''

    def __init__(self, address, handler_class=PostHandler):
        super().__init__(address, handler_class)

    def set_auth(self, username, password):
        self.key = base64.b64encode(
            bytes('%s:%s' % (username, password), 'utf-8')).decode('ascii')

    def get_auth_key(self):
        return self.key


if __name__ == '__main__':
    server = CustomHTTPServer((SERVER_HOST, SERVER_PORT))
    # server.set_auth('demo', 'demo')
    # server.socket = ssl.wrap_socket(server.socket,
    #                                keyfile=SERVER_KEY_FILE,
    #                                certfile=SERVER_CERT_FILE, server_side=True)
    print('Start server {}:{}'.format(SERVER_HOST, SERVER_PORT))
    server.serve_forever()

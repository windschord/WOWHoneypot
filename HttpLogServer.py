# -*- coding: utf-8 -*-
import base64
import cgi
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

from utils import EshHelper, RequestParser

from utils import EshHelper, RequestParser

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8888
SERVER_KEY_FILE = 'cert/server.key'
SERVER_CERT_FILE = 'cert/server.crt'
ES_HOST = 'localhost'
ES_PORT = 9200
ES_INDEX = 'wowhoneypot'
ES_TYPE = 'wowhoneypot'
# if enable GeoIP, set path to GeoLite2-City.mmdb
GEOIP_PATH = None  # 'GeoLite2-City.mmdb'

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

        payload = RequestParser().http(message)
        payload['pot_ip'] = pot_ip
        EshHelper(ES_HOST, ES_PORT, ES_INDEX, ES_TYPE).send(payload)


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

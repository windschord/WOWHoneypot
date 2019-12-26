# -*- coding: utf-8 -*-
import base64
import cgi
import json
import ssl
from http.server import HTTPServer, BaseHTTPRequestHandler

from config import *
from utils import EsHelper, RequestParser, GeoIpHelper


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
            self._parse_post()
        else:
            self.do_AUTHHEAD()

            response = {
                'success': False,
                'error': 'Invalid credentials'
            }

            self.wfile.write(bytes(json.dumps(response), 'utf-8'))

    def _parse_post(self):
        # decode POST data
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     })
        # return response
        self.send_response(200)
        self.end_headers()

        # Filter received data
        # get message from post data, but it seems duplicate data in message and msg keys.
        # so first try to get message key and if not exit it, that case get from msg.
        pot_ip = self.client_address[0]
        level_no = int(form['levelno'].value)
        print('receive from {} level {}'.format(pot_ip, level_no))

        if 'message' in form.keys():
            message = form['message'].value
        if not message and 'msg' in form.keys():
            message = form['msg'].value

        if level_no == AccessLog:
            payload = RequestParser().http_access_log(message)
            payload['pot_ip'] = pot_ip

            if HTTP_LOG_PROXY_GEOIP_PATH:
                try:
                    payload['client_geoip'] = GeoIpHelper(HTTP_LOG_PROXY_GEOIP_PATH).get(payload['client_ip'])
                except Exception as e:
                    print('Cannot get GeoIP {} {}'.format(payload['client_ip'], e))
        elif level_no == HuntLog:
            print(message)
            payload = RequestParser().http_hunt_log(form['asctime'].value,  message)
            print(payload)
        else:
            print('Not match any support log level with {}'.format(level_no))
            return

        EsHelper(HTTP_LOG_PROXY_ES_SERVER[level_no]['host'],
                 HTTP_LOG_PROXY_ES_SERVER[level_no]['port'],
                 HTTP_LOG_PROXY_ES_SERVER[level_no]['index']
                 ).send(payload)


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
    server = CustomHTTPServer((HTTP_LOG_PROXY_SERVER_HOST, HTTP_LOG_PROXY_SERVER_PORT))
    server.set_auth(HTTP_LOG_PROXY_SERVER_BASIC_AUTH_ID, HTTP_LOG_PROXY_SERVER_BASIC_AUTH_PASSWORD)
    if HTTP_LOG_PROXY_SERVER_KEY_FILE and HTTP_LOG_PROXY_SERVER_CERT_FILE:
        server.socket = ssl.wrap_socket(server.socket,
                                        keyfile=HTTP_LOG_PROXY_SERVER_KEY_FILE,
                                        certfile=HTTP_LOG_PROXY_SERVER_CERT_FILE, server_side=True)
    print('Start server {}:{}'.format(HTTP_LOG_PROXY_SERVER_HOST, HTTP_LOG_PROXY_SERVER_PORT))
    server.serve_forever()

# -*- coding: utf-8 -*-
from http.server import HTTPServer, BaseHTTPRequestHandler

import cgi


class PostHandler(BaseHTTPRequestHandler):

    def do_POST(self):
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
        client_ip = self.client_address[0]
        print(client_ip)
        # フォームに POST されたデータを表示する
        if 'message' in form.keys():
            message = form['message'].value
        if not message and 'msg' in form.keys():
            message = form['msg'].value

        print(message)


if __name__ == '__main__':
    server = HTTPServer(('localhost', 8888), PostHandler)
    server.serve_forever()

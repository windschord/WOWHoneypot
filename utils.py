# -*- coding: utf-8 -*-
import json
import re
import urllib
from datetime import datetime, timezone


class RequestParser(object):
    def tcp(self, message):
        return self.base(message)

    def http(self, message):
        return self.base(message)

    def base(self, message):
        message_ret = list(re.match('\[(.+)\] (.+) (.+) \"(.+) (.+) (.+)\" (\d+) (.+) (.+)$', message).groups())
        message_ret[0] = datetime.strptime(message_ret[0], "%Y-%m-%d %H:%M:%S%z"
                                           ).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        message_label = ['@timestamp', 'client_ip', 'hostname', 'method', 'path', 'version', 'status_code',
                         'match_result', 'request_all']

        payload = dict(zip(message_label, message_ret))
        return payload


class EshHelper(object):
    def __init__(self, es_host, es_port, es_index, es_type):
        self.es_host = es_host
        self.es_port = es_port
        self.es_index = es_index
        self.es_type = es_type

    def send(self, payload):
        json_data = json.dumps(payload).encode("utf-8")
        invoke_url = "http://{host}:{port}/{index}/{type}".format(host=self.es_host, port=self.es_port,
                                                                  index=self.es_index, type=self.es_type)

        req = urllib.request.Request(invoke_url, data=json_data, method="POST",
                                     headers={'Content-type': 'application/json'})

        print('URL: {} DATA: {}'.format((invoke_url, json_data)))

        with urllib.request.urlopen(req) as response:
            the_page = response.read().decode("utf-8")
            print('res body: {}'.format(the_page))

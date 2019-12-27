#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re
from datetime import datetime, timezone


class RequestParser(object):
    def tcp_access_log(self, message):
        return self.__access_log_base(message)

    def http_access_log(self, message):
        return self.__access_log_base(message)

    def http_hunt_result_log(self, message):
        return json.loads(message)

    def __access_log_base(self, message):
        message_ret = list(re.match('\[(.+)\] (.+) (.+) \"(.+) (.+) (.+)\" (\d+) (.+) (.+)$', message).groups())
        message_ret[0] = datetime.strptime(message_ret[0], "%Y-%m-%d %H:%M:%S%z"
                                           ).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        message_label = ['@timestamp', 'client_ip', 'hostname', 'method', 'path', 'version', 'status_code',
                         'match_result', 'request_all']

        payload = dict(zip(message_label, message_ret))
        return payload

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from datetime import datetime, timezone


class RequestParser(object):
    def tcp_access_log(self, message):
        return self.__access_log_base(message)

    def http_access_log(self, message):
        return self.__access_log_base(message)

    def http_hunt_log(self, asctime, message):
        asctime = datetime.strptime(asctime, "%Y-%m-%d %H:%M:%S%z"
                                    ).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        client_ip, hit = message.split(' ', 1)
        r = hit.split(' ', 1)
        if len(r) != 1:
            cmd = r[0]
            url = r[1]
        else:
            cmd = None
            url = r[0]

        return {'@timestamp': asctime, 'client_ip': client_ip, 'command': cmd, 'target_url': url}

    def __access_log_base(self, message):
        message_ret = list(re.match('\[(.+)\] (.+) (.+) \"(.+) (.+) (.+)\" (\d+) (.+) (.+)$', message).groups())
        message_ret[0] = datetime.strptime(message_ret[0], "%Y-%m-%d %H:%M:%S%z"
                                           ).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        message_label = ['@timestamp', 'client_ip', 'hostname', 'method', 'path', 'version', 'status_code',
                         'match_result', 'request_all']

        payload = dict(zip(message_label, message_ret))
        return payload

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import requests


class SlackWebHookNotify(object):
    def __init__(self, url):
        self.url = url

    def build_vt_check_error(self, error_time, pot_ip, target):
        return {
            "attachments": [
                {
                    "color": "#D00000",
                    "fields": [
                        {
                            "title": "Failed check hunting url risk",
                            "value": "TIME: {}\nPOT: {}\nTARGRT: {}".format(error_time, pot_ip, target),
                            "short": False
                        }
                    ]
                }
            ]
        }

    def send(self, message):
        headers = {
            'Content-Type': 'application/json'
        }

        r = requests.post(url=self.url, headers=headers, data=json.dumps(message))

        print('send to {}'.format(self.url))

        r.raise_for_status()


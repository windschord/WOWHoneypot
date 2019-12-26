# -*- coding: utf-8 -*-
import hashlib
import json
import re
import time
import urllib
import urllib.request
from datetime import datetime, timezone

import geoip2.database
import requests


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

        return {'@timestamp': asctime, 'client_ip': client_ip, 'command': cmd, 'url': url}

    def __access_log_base(self, message):
        message_ret = list(re.match('\[(.+)\] (.+) (.+) \"(.+) (.+) (.+)\" (\d+) (.+) (.+)$', message).groups())
        message_ret[0] = datetime.strptime(message_ret[0], "%Y-%m-%d %H:%M:%S%z"
                                           ).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        message_label = ['@timestamp', 'client_ip', 'hostname', 'method', 'path', 'version', 'status_code',
                         'match_result', 'request_all']

        payload = dict(zip(message_label, message_ret))
        return payload


class GeoIpHelper(object):
    def __init__(self, db_path):
        self.db_path = db_path

    def get(self, ip_address):
        with geoip2.database.Reader(self.db_path) as reader:
            response = reader.city(ip_address)
            return {
                'country': response.country.name,
                'city': response.city.name,
                'location': {
                    'lat': response.location.latitude,
                    'lon': response.location.longitude
                }
            }


class EsHelper(object):
    def __init__(self, es_host, es_port, es_index, es_type='_doc'):
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

        print('URL: {} DATA: {}'.format(invoke_url, json_data))

        with urllib.request.urlopen(req) as response:
            the_page = response.read().decode("utf-8")
            print('res body: {}'.format(the_page))


class VirusTotalHelper(object):
    def __init__(self, api_key):
        self.api_key = api_key

    def report(self, url):
        if len(url) == 0 and not url.startswith("http"):
            return None

        headers = {
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Trident/7.0; rv:11.0) like Gecko"
        }

        try:
            memory_cache = urllib.request.urlopen(url).read()
            filename = url[url.rindex("/") + 1:]
        except Exception as e:
            print("[ERROR] {0} - {1}".format(url, e))
            return None
        hash = hashlib.sha256(memory_cache).hexdigest()
        if len(filename) == 0:
            filename = hash
        params = {'apikey': self.api_key, 'resource': hash}

        response = requests.get('https://www.virustotal.com/vtapi/v2/file/report', params=params, headers=headers)
        json_response = response.json()

        print(
            "scan result response_code:{0}, scan hash: {1}, url:{2}".format(json_response['response_code'], hash, url))

        return json_response['response_code'], filename, memory_cache

    def check(self, url):
        response_code, filename, memory_cache = self.report(url)
        time.sleep(15)

        if response_code != 0:
            return

        print("submit: {0}".format(url))
        params = {'apikey': self.api_key}
        files = {'file': (filename, memory_cache)}
        response = requests.post('https://www.virustotal.com/vtapi/v2/file/scan', files=files, params=params)
        json_response = response.json()
        print(
            "response_code:{0}, permalink: {1}".format(json_response['response_code'], json_response['permalink']))
        time.sleep(15)

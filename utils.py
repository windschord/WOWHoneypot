# -*- coding: utf-8 -*-
import hashlib
import json
import re
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

        return {'@timestamp': asctime, 'client_ip': client_ip, 'command': cmd, 'target_url': url}

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

    def send(self, payload, is_update=False, es_id=''):
        json_data = json.dumps(payload).encode("utf-8")
        if is_update:
            invoke_url = "http://{host}:{port}/{index}/_update/{id}".format(host=self.es_host, port=self.es_port,
                                                                            index=self.es_index, id=es_id)
        else:
            invoke_url = "http://{host}:{port}/{index}/{type}".format(host=self.es_host, port=self.es_port,
                                                                      index=self.es_index, type=self.es_type)

        req = urllib.request.Request(invoke_url, data=json_data, method="POST",
                                     headers={'Content-type': 'application/json'})

        # print('URL: {} DATA: {}'.format(invoke_url, json_data))

        with urllib.request.urlopen(req) as response:
            the_page = response.read().decode("utf-8")
            # print('res body: {}'.format(the_page))

    def search(self, payload):
        json_data = json.dumps(payload).encode("utf-8")
        invoke_url = "http://{host}:{port}/{index}/_search".format(host=self.es_host, port=self.es_port,
                                                                   index=self.es_index, type=self.es_type)

        req = urllib.request.Request(invoke_url, data=json_data, method="GET",
                                     headers={'Content-type': 'application/json'})

        # print('URL: {} DATA: {}'.format(invoke_url, json_data))

        with urllib.request.urlopen(req) as response:
            the_page = json.loads(response.read().decode("utf-8"))
            # print('res body: {}'.format(the_page))
            return [[r['_id'], r['_source']] for r in the_page['hits']['hits']]


class VirusTotalHelper(object):
    def __init__(self, api_key):
        self.api_key = api_key

    @staticmethod
    def download_target(url):
        if len(url) == 0 and not url.startswith("http"):
            raise Exception('target url is wrong {}'.format(url))

        memory_cache = urllib.request.urlopen(url).read()
        target_hash = hashlib.sha256(memory_cache).hexdigest()

        file_name = url[url.rindex("/") + 1:]
        file_name = target_hash if len(file_name) == 0 else file_name

        return file_name, memory_cache, target_hash

    def report(self, target_hash):
        print('search report {}'.format(target_hash))

        url = 'https://www.virustotal.com/vtapi/v2/file/report'
        params = {'apikey': self.api_key, 'resource': target_hash}
        res = requests.get(url, params=params)
        res.raise_for_status()
        return res.json().get('response_code'), res.json().get('permalink')

    def scan(self, file_name, memory_cache):
        print('scan file {}'.format(file_name))

        url = 'https://www.virustotal.com/vtapi/v2/file/scan'
        params = {'apikey': self.api_key}
        files = {'file': (file_name, memory_cache)}

        res = requests.post(url, files=files, params=params)
        return res.json().get('response_code'), res.json().get('permalink')

    def check(self, url):
        file_name, memory_cache, target_hash = self.download_target(url)
        response_code, permalink = self.report(target_hash)

        if response_code == 0:
            response_code, permalink = self.report(file_name, memory_cache)

        print("scan result response_code:{}, permalink:{}".format(response_code, permalink))
        return file_name, target_hash, permalink

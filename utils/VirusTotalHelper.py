# -*- coding: utf-8 -*-
import hashlib
import ipaddress
import re
import urllib
import urllib.request
from logging import getLogger

import requests

logger = getLogger()


class VirusTotalHelper(object):
    def __init__(self, api_key):
        self.api_key = api_key

    @staticmethod
    def download_target(url):
        if len(url) == 0 and not url.startswith("http"):
            raise Exception('target url is wrong {}'.format(url))

        url = url.replace('\\', '')
        file_name = url[url.rindex("/") + 1:]

        # if target url is local address, end of search
        res = re.match('^http(|s)://(\d+\.\d+.\d+.\d+)', url)
        ip_address = res.group(2) if res else None
        if ip_address and ipaddress.ip_address(ip_address).is_private:
            logger.warning('request ip address is local address [{}]'.format(ip_address))
            return file_name, None, None

        try:
            memory_cache = urllib.request.urlopen(url).read()
        except Exception as e:
            print('target url is already gone. {}'.format(url))
            return file_name, None, None
        target_hash = hashlib.sha256(memory_cache).hexdigest()

        file_name = target_hash if len(file_name) == 0 else file_name

        return file_name, memory_cache, target_hash

    def report(self, target_hash):
        url = 'https://www.virustotal.com/vtapi/v2/file/report'
        params = {'apikey': self.api_key, 'resource': target_hash}
        res = requests.get(url, params=params)
        res.raise_for_status()
        return res.json().get('response_code'), res.json().get('permalink')

    def scan(self, file_name, memory_cache):
        url = 'https://www.virustotal.com/vtapi/v2/file/scan'
        params = {'apikey': self.api_key}
        files = {'file': (file_name, memory_cache)}

        res = requests.post(url, files=files, params=params)
        return res.json().get('response_code'), res.json().get('permalink')

    def check(self, url):
        file_name, memory_cache, target_hash = self.download_target(url)

        if not memory_cache:
            return file_name, None, None
        response_code, permalink = self.report(target_hash)

        if response_code == 0:
            response_code, permalink = self.report(file_name, memory_cache)

        return file_name, target_hash, permalink

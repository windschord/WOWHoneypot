#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from pprint import pprint

import requests

from utils import GeoIpHelper

r1 = requests.get(url='http://localhost:9200/wowhoneypot/wowhoneypot/_search?size=1000')
for i in r1.json()['hits']['hits']:
    gi = GeoIpHelper('GeoLite2-City.mmdb')

    header = {'Content-type': 'application/json'}

    if not i['_source'].get('client_geoip'):
        print('_id', i['_id'])
        print('client_ip', i['_source']['client_ip'])


        data = {
            'doc': {"client_geoip": gi.get(i['_source']['client_ip'])}
        }

        url = 'http://localhost:9200/wowhoneypot/wowhoneypot/{}/_update'.format(i['_id'])
        print(url)
        print(gi.get(i['_source']['client_ip']))
        print(json.dumps(data))
        r2 = requests.post(url, data=json.dumps(data), headers=header)
        print(r2.status_code, r2.text)
        # print('client_geoip', i['_source'].get('client_geoip'))

    # pprint(i)

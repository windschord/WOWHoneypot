# -*- coding: utf-8 -*-
import json
import urllib
import urllib.request


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

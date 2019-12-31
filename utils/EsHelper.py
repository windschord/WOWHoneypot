# -*- coding: utf-8 -*-
from logging import getLogger

from elasticsearch import Elasticsearch

logger = getLogger()


class EsHelper(object):
    def __init__(self, es_scheme, es_hosts, es_port, es_auth, es_index, es_type='_doc'):
        self.es = Elasticsearch(
            es_hosts,
            http_auth=es_auth,
            scheme=es_scheme,
            port=es_port,
        )
        self.es_index = es_index
        self.es_type = es_type

    def send(self, payload, es_id=None):
        res = self.es.index(index=self.es_index, doc_type=self.es_type, body=payload, id=es_id)
        logger.debug(res['result'])

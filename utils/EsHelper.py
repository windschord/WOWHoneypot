# -*- coding: utf-8 -*-
import glob
import os
import pickle
import re
import uuid
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
            timeout=1,
            dead_timeout=1,
            timeout_cutoff=1,
        )
        self.es_index = es_index
        self.es_type = es_type
        self.es_failed_store_dir ='es_failed'
        os.makedirs(self.es_failed_store_dir, exist_ok=True)

    def send(self, payload, es_id=None):
        try:
            res = self.es.index(index=self.es_index, doc_type=self.es_type, body=payload, id=es_id)
            logger.debug(res['result'])
            self.send_all_failed_data(es_id=es_id)
        except Exception as e:
            self.store_failed_data(payload=payload)

    def send_all_failed_data(self,  es_id=None):
        try:
            for f in self.__get_recovery_files():
                wip_file = '{}.wip'.format(f)
                logger.info('try to send data of {}.'.format(f))
                os.rename(f, wip_file)

                payload = self.load_failed_data(wip_file)
                res = self.es.index(index=self.es_index, doc_type=self.es_type, body=payload, id=es_id)
                logger.debug(res['result'])

                os.remove(wip_file)
                logger.info('successfully send data. backup file {} deleted.'.format(f))
        except Exception as e:
            logger.warning('sending local backup data failed. it will try next time.')

    def store_failed_data(self, payload):
        file_name = os.path.join(self.es_failed_store_dir, str(uuid.uuid4()))
        with open(file=file_name, mode='wb') as f:
            pickle.dump(obj=payload, file=f)
        logger.info('Data transmission failed. Saved to {}.'.format(file_name))

    def load_failed_data(self, file_path):
        with open(file=file_path, mode='rb') as f:
            return pickle.load(file=f)

    def __get_recovery_files(self):
        path = os.path.join(self.es_failed_store_dir, '*')
        ptn = re.compile('\.wip$')
        for p in glob.glob(path):
            if not p.endswith('.wip'):
                yield os.path.abspath(p)

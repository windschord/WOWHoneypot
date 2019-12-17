# -*- coding: utf-8 -*-
import logging

AccessLog = 21

class AccessLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == 21
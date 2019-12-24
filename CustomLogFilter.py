# -*- coding: utf-8 -*-
import logging

AccessLog = 21
HuntLog = 22


class AccessLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == AccessLog


class HuntLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == HuntLog

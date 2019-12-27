# -*- coding: utf-8 -*-
import logging

ACCESS_LOG = 21
HUNT_LOG = 22
HUNT_RESULT_LOG = 23


class AccessLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == ACCESS_LOG


class HuntLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == HUNT_LOG


class HuntResultLogFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == HUNT_RESULT_LOG

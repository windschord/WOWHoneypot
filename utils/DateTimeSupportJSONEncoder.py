#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from datetime import datetime


class DateTimeSupportJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super(DateTimeSupportJSONEncoder, self).default(o)

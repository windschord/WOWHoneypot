# -*- coding: utf-8 -*-
import ipaddress
from logging import getLogger

import geoip2.database

logger = getLogger()


class GeoIpHelper(object):
    def __init__(self, db_path):
        self.db_path = db_path

    def get(self, ip_address):
        if ipaddress.ip_address(ip_address).is_private:
            logger.warning('request ip address is local address [{}]'.format(ip_address))
            return None

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

# -*- coding: utf-8 -*-
import geoip2.database


class GeoIpHelper(object):
    def __init__(self, db_path):
        self.db_path = db_path

    def get(self, ip_address):
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

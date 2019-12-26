# -*- coding: utf-8 -*-
# --------------- WOWHONEYPOT settings ---------------
# default host: 0.0.0.0
from CustomLogFilter import AccessLog, HuntLog

WOWHONEYPOT_HOST = '0.0.0.0'

# default port: 8080
WOWHONEYPOT_PORT = 8080

# default server header: Apache
WOWHONEYPOT_SERVER_HEADER = 'Apache'

# art directory path
WOWHONEYPOT_ART_PATH = './art/'

# Access log separator
WOWHONEYPOT_LOG_SEPARATOR = " "

# Hunting
WOWHONEYPOT_HUNT_ENABLE = False

# for GDPR(True: replace source ip address with 0.0.0.0)
WOWHONEYPOT_IPMASKING = False

# --------------- HTTP log proxy settings ---------------
# default host: 0.0.0.0
HTTP_LOG_PROXY_SERVER_HOST = '0.0.0.0'

# default port: 8888
HTTP_LOG_PROXY_SERVER_PORT = 8888

# default basic auth user id: demo
# if you change this value, also you should change at logging_conf.py
HTTP_LOG_PROXY_SERVER_BASIC_AUTH_ID = 'demo'

# default basic auth password: demo
# if you change this value, also you should change at logging_conf.py
HTTP_LOG_PROXY_SERVER_BASIC_AUTH_PASSWORD = 'demo'

# default ssl server key: None
HTTP_LOG_PROXY_SERVER_KEY_FILE = None

# default ssl server cert: None
HTTP_LOG_PROXY_SERVER_CERT_FILE = None

# elastic search settings. http log proxy can handle multiple log level.
HTTP_LOG_PROXY_ES_SERVER = {
    AccessLog: {
        'host': 'localhost',
        'port': 9200,
        'index': 'wowhoneypot',
    },
    HuntLog: {
        'host': 'localhost',
        'port': 9200,
        'index': 'wowhoneypot_hunt',
    },
}

# if enable GeoIP, set path to GeoLite2-City.mmdb
# default GeoIP path: None
HTTP_LOG_PROXY_GEOIP_PATH = None

HTTP_LOG_PROXY_HUNT_POLLING_SEC = 60

HTTP_LOG_PROXY_VirusTotal_API_KEY = ''

# --------------- TCP log proxy settings ---------------
# default host: 0.0.0.0
TCP_LOG_PROXY_HOST = '0.0.0.0'

# default port: 8888
TCP_LOG_PROXY_PORT = 8888

# default elastic search host: localhost
TCP_LOG_PROXY_ES_HOST = 'localhost'

# default elastic search port: 9200
TCP_LOG_PROXY_ES_PORT = 9200

# default elastic search index: wowhoneypot
TCP_LOG_PROXY_ES_INDEX = 'wowhoneypot'

# if enable GeoIP, set path to GeoLite2-City.mmdb
# default GeoIP path: None
TCP_LOG_PROXY_GEOIP_PATH = None

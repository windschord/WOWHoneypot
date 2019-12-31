# -*- coding: utf-8 -*-
# --------------- WOWHONEYPOT settings ---------------
# default host: 0.0.0.0
WOWHONEYPOT_HOST = '0.0.0.0'

# default port: 8080
WOWHONEYPOT_PORT = 8080

# default server header: Apache
WOWHONEYPOT_SERVER_HEADER = 'Apache'

# art directory path
# default path: ./art/
WOWHONEYPOT_ART_PATH = './art/'

# Access log separator
# default separator: " "
WOWHONEYPOT_LOG_SEPARATOR = " "

# for GDPR(True: replace source ip address with 0.0.0.0)
WOWHONEYPOT_IPMASKING = False

# Hunting
# default: False
WOWHONEYPOT_HUNT_ENABLE = False

# Hunting target queue
# default: hunting_queue.db
WOWHONEYPOT_HUNT_QUEUE_DB = 'hunting_queue.db'

# default VirusTotal polling sec: 60 (1min)
VIRUSTOTAL_POLLING_SEC = 60

# default VirusTotal api key:
WOWHONEYPOT_VirusTotal_API_KEY = None

# default elastic search scheme: http
ES_SERVER_SCHEME = 'http'

# default elastic search hosts: http
ES_SERVER_HOSTS = ['localhost']

# default elastic search port: 9200
ES_SERVER_PORT = 9200

# default elastic search auth: None
# if you use auth, replace None to ('user', 'password')
ES_SERVER_AUTH = None

# default elastic search access log index: wowhoneypot
ES_SERVER_ACCESS_LOG_INDEX = 'wowhoneypot'

# default elastic search hunting log index: wowhoneypot_hunt
ES_SERVER_HUNT_LOG_INDEX = 'wowhoneypot_hunt'

# if enable GeoIP, set path to GeoLite2-City.mmdb
# default GeoIP path: None
GEOIP_PATH = None

# default slack webhook url: None
SLACK_WEBHOOK_URL = None

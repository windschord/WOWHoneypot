#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# Welcome to Omotenashi Web Honeypot(WOWHoneypot)
import base64
import json
import logging.handlers
import os
import random
import re
import select
import socket
import sys
import traceback
import urllib.parse
from datetime import datetime, timedelta, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer
from logging import config, getLogger
from threading import Thread
from time import sleep

import logging_conf
from config import *
from mrr_checker import parse_mrr
from utils.CustomLogFilter import HUNT_LOG, HUNT_RESULT_LOG, ACCESS_LOG
from utils.DateTimeSupportJSONEncoder import DateTimeSupportJSONEncoder
from utils.EsHelper import EsHelper
from utils.GeoIpHelper import GeoIpHelper
from utils.SlackWebHookNotify import SlackWebHookNotify
from utils.SqliteHelper import SqliteHelper
from utils.VirusTotalHelper import VirusTotalHelper

WOWHONEYPOT_VERSION = "20200229"

JST = timezone(timedelta(hours=+9), 'JST')
logger = getLogger(__name__)

hunt_rules = []
default_content = []
mrrdata = {}
mrrids = []
timeout = 3.0
blacklist = {}

pot_hostname = socket.gethostname()


class WOWHoneypotHTTPServer(ThreadingHTTPServer):
    def server_bind(self):
        HTTPServer.server_bind(self)
        self.socket.settimeout(timeout)

    def finish_request(self, request, client_address):
        request.settimeout(timeout)
        HTTPServer.finish_request(self, request, client_address)


class WOWHoneypotRequestHandler(BaseHTTPRequestHandler):
    def send_response(self, code, message=None):
        self.log_request(code)
        self.send_response_only(code, message)
        self.send_header('Date', self.date_time_string())
        self.error_message_format = "error"
        self.error_content_type = "text/plain"

    def handle_one_request(self):
        if WOWHONEYPOT_IPMASKING == True:
            clientip = "0.0.0.0"
        else:
            clientip = self.client_address[0]

        if not WOWHONEYPOT_IPMASKING and clientip in blacklist and blacklist[clientip] > 3:
            logging_system("Access from blacklist ip({0}). denied.".format(clientip), True, False)
            self.close_connection = True
            return
        try:
            (r, w, e) = select.select([self.rfile], [], [], timeout)
            if len(r) == 0:
                errmsg = "Client({0}) data sending was too late.".format(clientip)
                raise socket.timeout(errmsg)
            else:
                self.raw_requestline = self.rfile.readline(65537)
            if not self.raw_requestline:
                self.close_connection = True
                return

            rrl = str(self.raw_requestline, 'iso-8859-1')
            rrl = rrl.rstrip('\r\n')

            parse_request_flag = True
            if re.match("^[A-Z]", rrl) and (rrl.endswith("HTTP/1.0") or rrl.endswith("HTTP/1.1")):
                rrlmethod = rrl[:rrl.index(" ")]
                rrluri = rrl[rrl.index(" ") + 1:rrl.rindex(" ")].replace(" ", "%20")
                rrluri = rrluri.replace("\"", "%22")
                rrlversion = rrl[rrl.rindex(" ") + 1:]
                rrl2 = rrlmethod + " " + rrluri + " " + rrlversion
                self.raw_requestline = rrl2.encode()
            else:
                parse_request_flag = False

            if not self.parse_request() or not parse_request_flag:
                errmsg = "Client({0}) data cannot parse. {1}".format(clientip, str(self.raw_requestline))
                raise ValueError(errmsg)

            body = ""
            if 'content-length' in self.headers:
                content_len = int(self.headers['content-length'])
                if content_len > 0:
                    post_body = self.rfile.read(content_len)
                    body = post_body.decode()

            match = False
            for id in mrrids:
                if match:
                    break

                if "method" in mrrdata[id]["trigger"]:
                    if not self.command == mrrdata[id]["trigger"]["method"]:
                        continue

                uricontinue = False
                if "uri" in mrrdata[id]["trigger"]:
                    for u in mrrdata[id]["trigger"]["uri"]:
                        if re.search(u, self.path) is None:
                            uricontinue = True
                if uricontinue:
                    continue

                headercontinue = False
                if "header" in mrrdata[id]["trigger"]:
                    for h in mrrdata[id]["trigger"]["header"]:
                        if re.search(h, str(self.headers)) is None:
                            headercontinue = True
                if headercontinue:
                    continue

                bodycontinue = False
                if "body" in mrrdata[id]["trigger"]:
                    if len(body) == 0:
                        continue
                    for b in mrrdata[id]["trigger"]["body"]:
                        if re.search(b, body) is None:
                            bodycontinue = True
                if bodycontinue:
                    continue
                match = id

            status = 200
            tmp = self.requestline.split()
            if len(tmp) == 3:
                self.protocol_version = "{0}".format(tmp[2].strip())
            else:
                self.protocol_version = "HTTP/1.1"

            if not match:
                self.send_response(200)
                self.send_header("Server", WOWHONEYPOT_SERVER_HEADER)
                self.send_header('Content-Type', 'text/html')
                r = default_content[random.randint(0, len(default_content) - 1)]
                self.send_header('Content-Length', len(r))
                self.end_headers()
                self.wfile.write(bytes(r, "utf-8"))
            else:
                status = mrrdata[match]["response"]["status"]
                self.send_response(status)
                header_server_flag = False
                header_content_type_flag = False
                for name, value in mrrdata[match]["response"]["header"].items():
                    self.send_header(name, value)
                    if name == "Server":
                        header_server_flag = True
                    elif name == "Content-Type":
                        header_content_type_flag = True

                if not header_server_flag:
                    self.send_header('Server', WOWHONEYPOT_SERVER_HEADER)
                if not header_content_type_flag:
                    self.send_header('Content-Type', 'text/html')
                r = mrrdata[match]["response"]["body"]
                self.send_header('Content-Length', len(r))
                self.end_headers()
                self.wfile.write(bytes(r, "utf-8"))

            self.wfile.flush()

            # logging
            hostname = None
            if "host" in self.headers:

                if self.headers["host"].find(" ") == -1:
                    hostname = self.headers["host"]
                else:
                    hostname = self.headers["host"].split(" ")[0]
                if hostname.find(":") == -1:
                    hostname = hostname + ":80"
            else:
                hostname = "blank:80"

            request_all = self.requestline + "\n" + str(self.headers) + body
            logging_access(
                time=datetime.utcnow(),
                client_ip=clientip,
                hostname=hostname,
                request_line=self.requestline,
                status_code=status,
                match_result=match,
                request_all=base64.b64encode(request_all.encode('utf-8')).decode('utf-8'),
            )
            # Hunting
            if WOWHONEYPOT_HUNT_ENABLE:
                decoded_request_all = urllib.parse.unquote(request_all)
                hits = []
                for hunt_rule in hunt_rules:
                    hits.extend(re.findall(hunt_rule, decoded_request_all))
                logging_hunt(client_ip=clientip, hits=hits)

        except socket.timeout as e:
            emsg = "{0}".format(e)
            if emsg == "timed out":
                errmsg = "Session timed out. Client IP: {0}".format(clientip)
            else:
                errmsg = "Request timed out: {0}".format(emsg)
            self.log_error(errmsg)
            self.close_connection = True
            logging_system(errmsg, True, False)
            if clientip in blacklist:
                blacklist[clientip] = blacklist[clientip] + 1
            else:
                blacklist[clientip] = 1
            return
        except Exception as e:
            errmsg = "Request handling Failed: {0} - {1}".format(type(e), e)
            self.close_connection = True
            logging_system(errmsg, True, False)
            if clientip in blacklist:
                blacklist[clientip] = blacklist[clientip] + 1
            else:
                blacklist[clientip] = 1
            return


def format_access_log(time, client_ip, hostname, request_line, status_code, match_result, request_all, separator):
    return "[{time:%Y-%m-%d %H:%M:%S%z}]{s}{clientip}{s}{hostname}{s}\"{requestline}\"{s}{status_code}{s}{match_result}{s}{requestall}".format(
        time=time,
        clientip=client_ip,
        hostname=hostname,
        requestline=request_line,
        status_code=status_code,
        match_result=match_result,
        requestall=base64.b64encode(request_all.encode('utf-8')).decode('utf-8'),
        s=separator
    )


def logging_access(time, client_ip, hostname, request_line, status_code, match_result, request_all):
    log = format_access_log(time, client_ip, hostname, request_line, status_code, match_result, request_all,
                            WOWHONEYPOT_LOG_SEPARATOR)
    logger.log(ACCESS_LOG, log)

    if is_active_syslog():
        logger.log(msg="{0} {1}".format(__file__, log), level=logging.INFO)

    tmp = request_line.split()
    payload = {'@timestamp': time.strftime("%Y-%m-%dT%H:%M:%SZ"),
               'client_ip': client_ip,
               'client_geoip': None,
               'hostname': hostname,
               'method': tmp[0],
               'path': tmp[1],
               'version': tmp[2],
               'status_code': status_code,
               'match_result': match_result,
               'request_all': request_all,
               'pot_ip': WOWHONEYPOT_POT_IP
               }

    if GEOIP_PATH:
        try:
            payload['client_geoip'] = GeoIpHelper(GEOIP_PATH).get(payload['client_ip'])
        except Exception as e:
            print('Cannot get GeoIP {} {}'.format(payload['client_ip'], e))

    if ES_SERVER_HOSTS:
        EsHelper(ES_SERVER_SCHEME, ES_SERVER_HOSTS, ES_SERVER_PORT, ES_SERVER_AUTH, ES_SERVER_ACCESS_LOG_INDEX).send(
            payload)


def logging_system(message, is_error, is_exit):
    if not is_error:  # CYAN
        logger.info(message)
    else:  # RED
        logger.error(message)

    if is_exit:
        sys.exit(1)


# Hunt
def logging_hunt(client_ip, hits):
    SqliteHelper(WOWHONEYPOT_HUNT_QUEUE_DB).put_all(client_ip, hits)
    for hit in hits:
        logger.log(HUNT_LOG, "{clientip} {hit}".format(clientip=client_ip, hit=hit))


def get_time():
    return "{0:%Y-%m-%d %H:%M:%S%z}".format(datetime.now(JST))


def config_load():
    # art directory Load
    if not os.path.exists(WOWHONEYPOT_ART_PATH) or not os.path.isdir(WOWHONEYPOT_ART_PATH):
        logging_system("{0} directory load error.".format(WOWHONEYPOT_ART_PATH), True, True)

    defaultfile = os.path.join(WOWHONEYPOT_ART_PATH, "mrrules.xml")
    if not os.path.exists(defaultfile) or not os.path.isfile(defaultfile):
        logging_system("{0} file load error.".format(defaultfile), True, True)

    logging_system("mrrules.xml reading start.", False, False)

    global mrrdata
    mrrdata = parse_mrr(defaultfile, os.path.split(defaultfile)[0])

    global mrrids
    mrrids = sorted(list(mrrdata.keys()), reverse=True)

    if mrrdata:
        logging_system("mrrules.xml reading complete.", False, False)
    else:
        logging_system("mrrules.xml reading error.", True, True)

    defaultlocal_file = os.path.join(WOWHONEYPOT_ART_PATH, "mrrules_local.xml")
    if os.path.exists(defaultlocal_file) and os.path.isfile(defaultlocal_file):
        logging_system("mrrules_local.xml reading start.", False, False)
        mrrdata2 = parse_mrr(defaultlocal_file, os.path.split(defaultfile)[0])

        if mrrdata2:
            logging_system("mrrules_local.xml reading complete.", False, False)
        else:
            logging_system("mrrules_local.xml reading error.", True, True)

        mrrdata.update(mrrdata2)
        mrrids = sorted(list(mrrdata.keys()), reverse=True)

    artdefaultpath = os.path.join(WOWHONEYPOT_ART_PATH, "default")
    if not os.path.exists(artdefaultpath) or not os.path.isdir(artdefaultpath):
        logging_system("{0} directory load error.".format(artdefaultpath), True, True)

    global default_content
    for root, dirs, files in os.walk(artdefaultpath):
        for file in files:
            if not file.startswith(".") and file.endswith(".html"):
                tmp = open(os.path.join(artdefaultpath, file), 'r')
                default_content.append(tmp.read().strip())
                tmp.close()

    if len(default_content) == 0:
        logging_system("default html content not exist.", True, True)

    # Hunting
    if WOWHONEYPOT_HUNT_ENABLE:
        huntrulefile = os.path.join(WOWHONEYPOT_ART_PATH, "huntrules.txt")
        if not os.path.exists(huntrulefile) or not os.path.isfile(huntrulefile):
            logging_system("{0} file load error.".format(huntrulefile), True, True)

        with open(huntrulefile, 'r') as f:
            for line in f:
                line = line.rstrip()
                if len(line) > 0:
                    hunt_rules.append(line)


def is_active_syslog():
    return logging.handlers.SysLogHandler in [type(a) for a in logging.getLogger().manager.root.handlers]


def watch_hunting_log():
    if VIRUSTOTAL_API_KEY:
        vth = VirusTotalHelper(VIRUSTOTAL_API_KEY)
    sql = SqliteHelper(WOWHONEYPOT_HUNT_QUEUE_DB)
    slack = SlackWebHookNotify(SLACK_WEBHOOK_URL)
    if ES_SERVER_HOSTS:
        es = EsHelper(ES_SERVER_SCHEME, ES_SERVER_HOSTS, ES_SERVER_PORT, ES_SERVER_AUTH, ES_SERVER_HUNT_LOG_INDEX)
    sleep(15)

    while True:
        logging_system("check new hunting", False, False)
        if sql.pull_one():
            db_id, asctime, client_ip, hit = sql.pull_one()
            logging_system("check hunting target [{}]".format(db_id), False, False)
            try:
                reg = re.match('^(.+)(http.+)$', hit)
                if reg:
                    cmd, target_url = reg.groups()
                else:
                    cmd = None
                    target_url = hit

                if VIRUSTOTAL_API_KEY:
                    file_name, target_hash, permalink = vth.check(target_url)
                else:
                    file_name = None
                    target_hash = None
                    permalink = None

                payload = {
                    '@timestamp': asctime.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    'client_ip': client_ip,
                    'row_data': hit,
                    'command': cmd,
                    'target_url': target_url,
                    'target_file_name': file_name,
                    'target_hash': target_hash,
                    'vt_permalink': permalink,
                    'pot_ip': WOWHONEYPOT_POT_IP
                }

                logger.log(HUNT_RESULT_LOG, json.dumps(payload, cls=DateTimeSupportJSONEncoder))
                if ES_SERVER_HOSTS:
                    es.send(payload)

                if permalink:
                    sql.delete_one(db_id)
                else:
                    sql.set_failed(db_id)
                    if SLACK_WEBHOOK_URL:
                        slack.send(slack.build_vt_check_error(asctime, pot_hostname, hit))
            except Exception as e:
                logging_system('Some Error {}'.format(e), True, False)
        logging_system("check new hunting: done", False, False)
        sleep(VIRUSTOTAL_POLLING_SEC)


if __name__ == '__main__':
    random.seed(datetime.now())

    config.dictConfig(logging_conf.conf)
    try:
        config_load()
    except Exception:
        print(traceback.format_exc())
        sys.exit(1)
    logging_system(
        "WOWHoneypot(version {0}) start. {1}:{2} at {3}".format(WOWHONEYPOT_VERSION, WOWHONEYPOT_HOST, WOWHONEYPOT_PORT,
                                                                get_time()),
        False, False)
    logging_system("Hunting: {0}".format(WOWHONEYPOT_HUNT_ENABLE), False, False)
    logging_system("IP Masking: {0}".format(WOWHONEYPOT_IPMASKING), False, False)
    myServer = WOWHoneypotHTTPServer((WOWHONEYPOT_HOST, WOWHONEYPOT_PORT), WOWHoneypotRequestHandler)
    myServer.timeout = timeout

    if WOWHONEYPOT_HUNT_ENABLE:
        SqliteHelper(WOWHONEYPOT_HUNT_QUEUE_DB)
        if not VIRUSTOTAL_API_KEY:
            logging_system('Not set your api key at VIRUSTOTAL_API_KEY. if you want use virustotal api, please set it.',
                           False, False)
        t = Thread(target=watch_hunting_log)
        t.start()
    try:
        myServer.serve_forever()
    except KeyboardInterrupt:
        pass

    myServer.server_close()
    if WOWHONEYPOT_HUNT_ENABLE:
        t.join()

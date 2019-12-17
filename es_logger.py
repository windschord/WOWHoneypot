import urllib.request, urllib.error
import datetime
import json
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class EsLogger(object):
  def __init__(self, es_host, es_port, es_index, es_type):
    self.es_host = es_host
    self.es_port = es_port
    self.es_index = es_index
    self.es_type = es_type


  def post_to_es(self, payload):
    json_data = json.dumps(payload).encode("utf-8")
    invoke_url = "http://{host}:{port}/{index}/{type}".format(host=self.es_host, port=self.es_port, index=self.es_index, type=self.es_type)

    req = urllib.request.Request(invoke_url, data=json_data, method="POST", headers={'Content-type': 'application/json'})
    try:
      with urllib.request.urlopen(req) as response:
        the_page = response.read().decode("utf-8")
        print('res body   :{}'.format(the_page))
    except Exception as e:
      print(e)


if __name__ == '__main__':
  data = {
      "@timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
      "payload"   : 'test'
  }
  EsLogger('sakura01.windschord.com', 9200, 'test', 'test').post_to_es(data)

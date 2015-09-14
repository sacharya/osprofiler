import eventlet
eventlet.monkey_patch()
import log
from handler import Handler
import time
import utils

from python_blueflood.client import Blueflood
from python_blueflood.client import utils

logger = log.get_logger()


class BluefloodHandler(Handler):
    
    def __init__(self, *args, **kwargs):
        super(BluefloodHandler, self).__init__(*args, **kwargs)
        auth_url = self.config['auth']['auth_url']
        apikey = self.config['auth']['apikey']
        username = self.config['auth']['username']
        client = Blueflood(auth_url=auth_url, apikey=apikey, username=username)
        self.queue = eventlet.queue.Queue()
        self.worker = BluefloodWorker(self.queue, client)

    def handle(self, data):
        ms = utils.time_in_ms()
        for d in data.get('metrics'):
            for k, v in d.iteritems():
                entry ={"ttlInSeconds": 18, "collectionTime": ms, 
                        "metricName": "%s.%s" % (self.host_id, k), 
                            "metricValue": v}
                self.queue.put(entry)

class BluefloodWorker(object):

    def __init__(self, queue, client):
        self.queue = queue
        self.client = client
        self.batch_size = 100

    def work(self):
        while True:
            data = []
            count = 0
            for i in xrange(self.batch_size):
                try:
                    logger.debug("Blueflood Queue size is: %s " %
                            self.queue.qsize())
                    entry = self.queue.get(block=False)
                    count = count + 1
                    data.append(entry)
                except eventlet.queue.Empty:
                    time.sleep(1)

            logger.info("Got %s docs" % len(data))
            if data:
                try:
                    self.client.ingest(data)
                    for i in xrange(len(data)):
                        self.queue.task_done()
                    logger.info("Processed %s entries to blueflood" % len(data))
                except Exception as e:
                    logger.exception(str(data))
                    logger.exception("Error submitting to blueflood")
                    raise e
            time.sleep(1)

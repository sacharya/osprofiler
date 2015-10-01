import eventlet
import logging
import time

from bluefloodclient.client import Blueflood

from osprofiler import utils
from handler import Handler, Worker

logger = logging.getLogger('osprofiler.%s' % __name__)


class BluefloodHandler(Handler):

    def __init__(self, *args, **kwargs):
        super(BluefloodHandler, self).__init__(*args, **kwargs)
        auth_url = self.config['auth']['auth_url']
        apikey = self.config['auth']['apikey']
        username = self.config['auth']['username']
        client = Blueflood(auth_url=auth_url, apikey=apikey, username=username)
        self.queue = eventlet.queue.Queue()
        self.worker = BluefloodWorker(self.queue, client, config=self.config)

    def handle(self, data):
        ms = utils.time_in_ms()
        for d in data.get('metrics'):
            entry = {
                "ttlInSeconds": 86400, "collectionTime": ms,
                "metricName": d['name'],
                "metricValue": d['value']
            }
            if d.get('units'):
                entry.update(unit=d.get('units'))
            self.queue.put(entry)


class BluefloodWorker(Worker):

    def __init__(self, queue, client, config=None):
        if config is None:
            config = {}
        self.queue = queue
        self.client = client
        self.batch_size = config.get('batch_size', 1000)

    def work(self):
        data = []
        logger.info("Blueflood Queue size is: %s " % self.queue.qsize())
        for i in xrange(self.batch_size):
            try:
                entry = self.queue.get(block=False)
                data.append(entry)
            except eventlet.queue.Empty:
                break

        logger.info("Got %s docs" % len(data))
        if data:
            try:
                start = utils.time_in_ms()
                self.client.ingest(data)
                for i in xrange(len(data)):
                    self.queue.task_done()
                time_taken = (utils.time_in_ms() - start)
                logger.info("Processed %s entries to blueflood. Took %s ms \
                            " % (len(data), time_taken))
            except Exception:
                logger.exception("Error submitting to blueflood")

        # Sleep if we hit the empty queue
        if len(data) < self.batch_size:
            time.sleep(1)

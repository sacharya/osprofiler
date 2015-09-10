import eventlet
eventlet.monkey_patch()
import log
from handler import Handler
import time


from python_blueflood.client import Blueflood
from python_blueflood.client import utils

logger = log.get_logger()


class BluefloodHandler():
    
    def __init__(self, *args, **kwargs):
        self.config = kwargs.get('config')
        auth_url = self.config['auth']['auth_url']
        apikey = self.config['auth']['apikey']
        username = self.config['auth']['username']
        client = Blueflood(auth_url=auth_url, apikey=apikey, username=username)
        self.queue = eventlet.queue.Queue()
        self.worker = BluefloodWorker(self.queue, client)

    def handle(self, data):
        self.queue.put(data)

class BluefloodWorker(object):

    def __init__(self, queue, client):
        self.queue = queue
        self.client = client
        self.batch_size = 5

    def work(self):
        while True:
            data = []
            count = 0
            for i in xrange(self.batch_size):
                try:
                    logger.debug("Blueflood Queue size is: %s " %
                            self.queue.qsize())
                    entries = self.queue.get(block=False)
                    count = count + 1
                    for entry in entries:
                        data.append(entry)
                except eventlet.queue.Empty:
                    time.sleep(1)

            logger.info("Got %s docs" % len(data))
            if data:
                try:
                    self.client.ingest(data)
                    for i in xrange(count):
                        self.queue.task_done()
                    logger.info("Processed %s entries to blueflood" % len(data))
                except Exception as e:
                    logger.exception("Error submitting to blueflood")
                    raise e
            time.sleep(1)

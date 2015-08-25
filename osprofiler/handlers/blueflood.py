import eventlet
eventlet.monkey_patch()
from handler import Handler
import time


from python_blueflood.client import Blueflood
from python_blueflood.client import utils

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
        self.batch_size = 100

    def work(self):
        while True:
            data = []
            count = 0
            for i in xrange(self.batch_size):
                try:
                    print "Queue size is: %s " % self.queue.qsize()
                    data = []
                    entries = self.queue.get(block=False)
                    count = count + 1
                    for entry in entries:
                        data.append(entry)
                except eventlet.queue.Empty:
                    print "Empty queue"
                    time.sleep(1)
            print "Got %s data" % len(data)
            if data:
                client.ingest(data)
                for i in xrange(count):
                    self.queue.task_done()

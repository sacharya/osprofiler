import eventlet
eventlet.monkey_patch()
import time
import utils

import elasticsearch
from elasticsearch.helpers import bulk

client = elasticsearch.Elasticsearch(['192.168.4.22'])

class ElasticSearchHandler(object):

    def __init__(self):
        self.queue = eventlet.queue.Queue()
        self.worker = ElasticSearchWorker(self.queue, client)

    def handle(self, data):
        self.queue.put(data)

class ElasticSearchWorker(object):

    def __init__(self, queue, client):
        self.queue = queue
        self.client = client
        self.batch_size = 100

    def work(self):
        while True:
            docs = []
            for i in xrange(self.batch_size):
                try:
                    print "Queue size is: %s " % self.queue.qsize()
                    res = self.queue.get(block=False)
                    new_res = {}
                    if type(res) is list:
                        for item in res:
                            new_res.update
                    res.update(
                        _index='suda',
                        _type='random'
                    )
                    docs.append(res)
                except eventlet.queue.Empty:
                    print "Empty queue"
                    time.sleep(1)

            print "Got %s docs" % len(docs)
            if docs:
                try:
                    count, extra = bulk(self.client, docs)
                    print "Inserted %s %s" % (count, extra)
                    time.sleep(1)
                except elasticsearch.exceptions.RequestError as e:
                    print e
                    time.sleep(1)


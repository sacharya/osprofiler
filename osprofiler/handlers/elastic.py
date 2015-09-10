import eventlet
eventlet.monkey_patch()
import log
import time
import utils

import elasticsearch
from elasticsearch.helpers import bulk

logger = log.get_logger()

class ElasticSearchHandler(object):

    def __init__(self, *args, **kwargs):
        self.queue = eventlet.queue.Queue()
        client = elasticsearch.Elasticsearch(['192.168.4.22'])
        self.worker = ElasticSearchWorker(self.queue, client)

    def handle(self, data):
        self.queue.put(data)

class ElasticSearchWorker(object):

    def __init__(self, queue, client):
        self.queue = queue
        self.client = client
        self.batch_size = 5

    def work(self):
        while True:
            docs = []
            for i in xrange(self.batch_size):
                try:
                    logger.debug("ElasticSearch  Queue size is: %s " %
                            self.queue.qsize())
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
                    time.sleep(1)

            logger.info("Got %s docs" % len(docs))
            if docs:
                try:
                    count, extra = bulk(self.client, docs)
                    logger.info("Processed %s %s entries to elasticsearch" % (count, extra))
                except elasticsearch.exceptions.RequestError as e:
                    logger.exception("Error submitting to elasticsearch")
                    raise e
            time.sleep(1)


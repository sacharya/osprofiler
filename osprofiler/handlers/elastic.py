import eventlet
eventlet.monkey_patch()
import log
import time
import utils

import handler
import elasticsearch
from elasticsearch.helpers import bulk

logger = log.get_logger()

class ElasticSearchHandler(handler.Handler):

    def __init__(self, *args, **kwargs):
        super(ElasticSearchHandler, self).__init__(*args, **kwargs)
        self.queue = eventlet.queue.Queue()
        client = elasticsearch.Elasticsearch(['192.168.4.22'])
        self.worker = ElasticSearchWorker(self.queue, client)

    def handle(self, data):
        if data is None:
            return
        if isinstance(data, list):
            for d in data:
                self.queue.put(d)
        else:
            self.queue.put(data)

class ElasticSearchWorker(handler.Worker):

    def __init__(self, queue, client):
        self.queue = queue
        self.client = client
        self.batch_size = 100

    def work(self):
        logger.info("ElasticSearch  Queue size is: %s " %
                    self.queue.qsize())
        docs = []
        for i in xrange(self.batch_size):
            try:
                res = self.queue.get(block=False)
                res.update(
                    _index='intelcloud',
                    _type='random'
                )
                docs.append(res)
            except eventlet.queue.Empty:
                time.sleep(0.1)

        logger.info("Got %s elasticsearch docs" % len(docs))
        if docs:
            try:
                logger.debug(docs)
                start = utils.time_in_ms()
                count, extra = bulk(self.client, docs)
                time_taken = (utils.time_in_ms() - start)
                logger.info("Processed %s %s entries to elasticsearch. Took %s ms." % (count, extra, time_taken))
            except elasticsearch.exceptions.RequestError as e:
                logger.exception("Error submitting to elasticsearch")
                logger.exception(str(e))

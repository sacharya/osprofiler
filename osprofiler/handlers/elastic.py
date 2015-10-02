import eventlet
import logging
import time

from osprofiler import utils

import handler
from datetime import datetime
import elasticsearch
from elasticsearch.helpers import bulk


logger = logging.getLogger('osprofiler.%s' % __name__)
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


class ElasticSearchHandler(handler.Handler):

    def __init__(self, *args, **kwargs):
        super(ElasticSearchHandler, self).__init__(*args, **kwargs)
        self.queue = eventlet.queue.Queue()
        self.workers = []
        for i in xrange(self.config.get('workers', 1)):
            self.create_worker()

    def create_worker(self):
        """
        Creates a worker.

        @returns ElasticSearchWorker

        """
        worker = ElasticSearchWorker(self.queue, self.config)
        self.workers.append(worker)
        return worker

    def date_to_ms(self, source):
        return source['_context_timestamp'][:-3]

    def handle(self, data):
        if data is None:
            return
        if isinstance(data, list):
            for doc in data:
                doc.update(context_timestamp=self.date_to_ms(doc))
                self.queue.put(doc)
        else:
            data.update(context_timestamp=self.date_to_ms(data))
            self.queue.put(data)


class ElasticSearchWorker(handler.Worker):

    def __init__(self, queue, config=None):
        self.queue = queue
        if config is None:
            config = {}
        self.client = elasticsearch.Elasticsearch(
            [config.get('host', 'localhost')]
        )
        self.batch_size = config.get('batch_size', 100)
        self.index_prefix = config.get('index_prefix', 'yourcloud')
        self.index_type = config.get('index_type', 'event')

    def date_from_context(self, source):
        date = datetime.strptime(source['_context_timestamp'], TIME_FORMAT)
        return date.strftime("%Y-%m-%d")

    def work(self):
        logger.info("ElasticSearch  Queue size is: %s " %
                    self.queue.qsize())
        docs = []
        for i in xrange(self.batch_size):
            try:
                res = self.queue.get(block=False)
                format_date = self.date_from_context(res)
                res.update(
                    _index='%s.%s' % (self.index_prefix, format_date),
                    _type=self.index_type
                )
                docs.append(res)
            except eventlet.queue.Empty:
                break

        logger.info("Got %s elasticsearch docs" % len(docs))
        if docs:
            try:
                logger.debug(docs)
                start = utils.time_in_ms()
                count, extra = bulk(self.client, docs)
                time_taken = (utils.time_in_ms() - start)
                logger.info("Processed %s %s entries to elasticsearch. "
                            "Took %s ms." % (count, extra, time_taken))
            except elasticsearch.exceptions.RequestError:
                logger.exception("Error submitting to elasticsearch")

        if len(docs) < self.batch_size:
            time.sleep(1)

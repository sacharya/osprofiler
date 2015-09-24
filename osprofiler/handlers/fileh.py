import eventlet
eventlet.monkey_patch()
import logging
import time

logger = logging.getLogger('osprofiler.%s' % __name__)


class FileHandler(object):

    def __init__(self):
        self.queue = eventlet.queue.Queue()
        self.worker = FileWorker(self.queue)

    def handle(self, data):
        self.queue.put(data)


class FileWorker(object):

    def __init__(self, queue):
        self.queue = queue

    def work(self):
        while True:
            try:
                logger.debug("Queue size: %s " % self.queue.qsize())
                res = self.queue.get(block=False)
                self._save(res)
                time.sleep(1)
            except eventlet.queue.Empty:
                logger.debug("Empty queue")
                time.sleep(1)

    def _save(self, data):
        with open('output.file', 'a') as f:
            f.write("\n" + str(data))

import eventlet
eventlet.monkey_patch()
import time
import utils

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
                print "Queue size: %s " % self.queue.qsize()
                res = self.queue.get(block=False)
                self._save(res)
                time.sleep(1)
            except eventlet.queue.Empty:
                print "Empty queue"
                time.sleep(1)

    def _save(self, data):
        with open('output.file','a') as f:
            f.write("\n"+str(data))



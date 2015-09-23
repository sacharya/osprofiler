import logging
import utils

logger = logging.getLogger('osprofiler.%s' % __name__)


class Handler(object):

    def __init__(self, *args, **kwargs):
        self.config = kwargs.get('config')
        self.host_id = utils.host_identifier()


class Worker(object):

    def __init__(self):
        pass

    def work(self):
        pass

    def execute(self):
        while True:
            try:
                logger.info("Entering " + self.__class__.__name__ + ".work")
                self.work()
                logger.info("Leaving " + self.__class__.__name__ + ".work")
                raise Exception("Testing exception")
            except Exception:
                logger.warning("Exception running %s.work:" %
                               (self.__class__.__name__), exc_info=True)

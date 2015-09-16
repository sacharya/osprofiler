import log
import utils

logger = log.get_logger()


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
                logger.info("Entering " + self.__class__.__name__ +".work")
                self.work()
                logger.info("Leaving " + self.__class__.__name__ + ".work")
            except Exception as ex:
                logger.warning("Exception running %s: %s" % (self.__class__.__name__+ ".work", str(ex)))

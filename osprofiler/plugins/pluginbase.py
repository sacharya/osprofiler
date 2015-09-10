import eventlet
eventlet.monkey_patch()
import log
import handlers

import time
import utils


logger = log.get_logger()


class PluginBase(object):

    def __init__(self, *args, **kwargs):
        self.config = kwargs.get('config')
        self.handlers = kwargs.get('handlers')
        self.host_id = utils.host_identifier()

    def get_sample(self):
        pass

    def execute(self):
        while True:
            logger.debug("Entering " + self.__class__.__name__ + ".get_sample")
            data = self.get_sample()
            for handler in self.handlers:
                logger.info("Running %s for %s " % (str(handler),
                    self.__class__.__name__))
                handler.handle(data)
            logger.debug("Leaving " + self.__class__.__name__ + ".get_sample")
            time.sleep(self.config['push_interval'])
            

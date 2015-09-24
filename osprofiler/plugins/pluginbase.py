import eventlet
eventlet.monkey_patch()

import logging
import time

from osprofiler import utils

logger = logging.getLogger('osprofiler.%s' % __name__)


class PluginBase(object):

    def __init__(self, *args, **kwargs):
        self.config = kwargs.get('config')
        self.handlers = kwargs.get('handlers')
        self.host_id = utils.host_identifier()

    def get_sample(self):
        pass

    def execute(self):
        while True:
            try:
                logger.debug("Entering %s.get_sample"
                             % self.__class__.__name__)
                data = self.get_sample()
                for handler in self.handlers:
                    logger.info("Running %s for %s " %
                                (str(handler), self.__class__.__name__))
                    handler.handle(data)
                logger.debug("Leaving %s.get_sample" %
                             self.__class__.__name__)
            except Exception:
                logger.exception("Exception running %s.get_sample" %
                                 self.__class__.__name__)

            time.sleep(self.config['push_interval'])

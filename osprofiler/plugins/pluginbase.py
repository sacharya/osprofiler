import eventlet
eventlet.monkey_patch()
import handlers

import time

class PluginBase(object):

    def __init__(self, *args, **kwargs):
        self.config = args[1].get('config')
        self.handlers =  args[1].get('handlers')
        #self.config = kwargs.get('config')
        #self.handlers = kwargs.get('handlers')

    def get_sample(self):
        pass

    def execute(self):
        while True:
            print "Entering " + self.__class__.__name__ + ".get_sample"
            data = self.get_sample()
            for handler in self.handlers:
                print "Running %s for %s " % (str(handler), self.__class__.__name__)
                handler.handle(data)
            print "Leaving " + self.__class__.__name__ + ".get_sample"
            time.sleep(self.config['push_interval'])
            

#!/usr/bin/env python
import eventlet
eventlet.monkey_patch()
import log
import time
import utils

from args import get_args
from plugin_loader import PluginLoader

logger = log.get_logger('osprofiler')


class Application:
    def __init__(self, config):
        self.config = config
        loader = PluginLoader(config)
        plugins, handlers = loader.load_plugins()
        self.plugins = plugins
        self.handlers = handlers

    def process(self):
        try:
            pool = eventlet.greenpool.GreenPool()
            handlers = []
            for agent in self.config['agents']:
                if agent['name'] in self.plugins:
                    plugin = self.plugins[agent['name']]
                    if plugin.handlers:
                        pool.spawn(plugin.execute)
                        time.sleep(0.1)
                        handlers.extend(plugin.handlers)
            handlers = list(set(handlers))
            for handler in handlers:
                worker = handler.worker
                logger.info("Running worker %s " % worker)
                pool.spawn(worker.execute)
                time.sleep(0.1)

            pool.waitall()
        except Exception as ex:
            logger.exception("Exception occured: %s" % str(ex))


def main():
    args = get_args()
    config = utils.read_config(args.config)
    app = Application(config)
    app.process()

if __name__ == '__main__':
    main()

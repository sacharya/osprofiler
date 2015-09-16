# TODO: Put each function call on it's own thread?
import eventlet
eventlet.monkey_patch()
import log
import os
import psutil
import sys
import time
import utils


# GLOBAL CONSTANTS
CONFIG_FILE = "/etc/osprofiler/osprofiler.conf"
LOG_FILE = "/var/log/osprofiler.log"
PLUGINS = "plugins"

logger = log.get_logger()


class PluginLoader:
    def __init__(self, config):
        self.config = config
        self.agent_list = config['agents']
        self.backend_list = config['backend']

    def load_plugins(self):
        """
        Import the modules for the plugins specified in the
        config file, instantiate a class, and store it in
        a dict with it's name reference as the key
        """

        backend_dict = {}
        for backend in self.backend_list:
            backend_dict[backend['name']] = self.load_object(backend)

        agent_dict = {}
        for agent in self.agent_list:
            handlers = []
            if 'handlers' in agent:
                handler_keys = agent['handlers']
                for handler in agent['handlers'].split(","):
                    handler = backend_dict[handler]
                    handlers.append(handler)
            agent_dict[agent['name']] = self.load_object(agent, handlers=handlers)
        return [agent_dict, backend_dict]

    def load_object(self, params, handlers=None):
        full_name = params['plugin']
        try:
            mod_name, class_name = full_name.split(".", 1)[1].rsplit(".", 1)
            mod = __import__(mod_name, fromlist=[class_name])
            klass = getattr(mod, class_name)
            args = []
            kwargs = {"config":params, "handlers":handlers}
            logger.info("Loaded klass %s with kwargs %s " % (klass, kwargs))
            return klass(*args, **kwargs)
        except Exception as ex:
            logger.exception("Unable to load all plugins and handlers. Check \
                    your config.")
            raise ex

class Application:
    def __init__(self, config):
        self.config = config
        self.push_interval = config['push_interval']
        loader = PluginLoader(config)
        plugins, handlers = loader.load_plugins()
        self.plugins = plugins
        self.handlers = handlers

    def process(self):
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

def main():
    config = utils.readConfig()
    app = Application(config)
    app.process()

if __name__ == '__main__':
    main()

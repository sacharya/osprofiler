# TODO: Put each function call on it's own thread?
import logging

logger = logging.getLogger('osprofiler.%s' % __name__)


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
                for handler in agent['handlers']:
                    handler = backend_dict[handler]
                    handlers.append(handler)
            agent_dict[agent['name']] = self.load_object(agent,
                                                         handlers=handlers)
        return [agent_dict, backend_dict]

    def load_object(self, params, handlers=None):
        full_name = params['plugin']
        try:
            mod_name, class_name = full_name.rsplit(".", 1)
            mod = __import__(mod_name, fromlist=[class_name])
            klass = getattr(mod, class_name)
            kwargs = {"config": params, "handlers": handlers}
            logger.info("Loaded klass %s with kwargs %s " % (klass, kwargs))
            return klass(**kwargs)
        except Exception as ex:
            logger.exception("Unable to load all plugins and handlers. Check \
                    your config.")
            raise ex

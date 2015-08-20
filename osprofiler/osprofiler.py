# TODO: Put each function call on it's own thread?

import os
import psutil
import sys
import time
import yaml


# GLOBAL CONSTANTS
CONFIG_FILE = "/etc/osprofiler/osprofiler.conf"
LOG_FILE = "/var/log/osprofiler.log"
PLUGINS = "plugins"

class PluginLoader:
    def __init__(self, config):
        self.config = config
        self.agent_list = config['agents']

    def load_plugins(self):
        """
        Import the modules for the plugins specified in the
        config file, instantiate a class, and store it in
        a dict with it's name reference as the key
        """

        agent_object_dict = {}
        sys.path.insert(0, PLUGINS)
        for agent in self.agent_list:
            try:
                loaded_mod = __import__(agent['plugin'])
                class_name =  self._get_class_name( agent['plugin'])
                # Load class from imported module, instantiate an object,  and store it in dict
                agent_object_dict[agent['name']] = getattr(loaded_mod, class_name)(agent)
                print "Loaded %s " % agent['plugin']
            except Exception as ex:
                print "Error loading :"
                print str(ex)
                pass

        # Will end up with something looking like:
        # { "mysqlagent1": <OBJ>, "systemagent1": <OBJ> }
        return agent_object_dict

    def _get_class_name(self, mod_name):
        output = mod_name.title()
        return output


class Worker:
    def __init__(self, config):
        self.config = config
        self.push_interval = config['push_interval']
        loader = PluginLoader(config)
        self.plugins = loader.load_plugins()

    def work(self):
        while True:
            for agent in self.config['agents']:
                if agent['name'] in self.plugins:
                    plugin = self.plugins[agent['name']]
                    plugin.get_sample()
            time.sleep(self.push_interval)


def _readConfig():
    """Read values from configuration file."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = f.read()
    except IOError:
        print "Unable to read from the configuration file %s" % CONFIG_FILE
    try:
        return yaml.load(config)
    except yaml.parser.Error:
        return "ERROR: Failed to read configuration file. Invalid yaml."

def main():
    config = _readConfig()
    worker = Worker(config)
    worker.work()

if __name__ == '__main__':
    main()

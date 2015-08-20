# TODO: Put each function call on it's own thread?

import os
import psutil
import time
import yaml

# GLOBAL CONSTANTS
CONFIG_FILE = "/etc/osprofiler/osprofiler.conf"
LOG_FILE = "/var/log/osprofiler.log"


def main():
    """Run the main application."""
    # Variables
    # Reading the configuration file
    configDict = _readConfig()
    push_interval = configDict['push_interval']

    # List of agents specificed in the config
    agent_list = configDict['agents']

    # Each agent entry looks like:
    '''
    agents:
      - plugin: cipsystem
        name: "systemagent1"
        metrics:
          - network
          - cpu
          - memory
    '''

    # Import pythong modules for each agent and instantiate an object
    agent_object_dict = _import_agents(agent_list)

    while (True):
        for agent in agent_list:
            agent_object = agent_object_dict[agent['name']]
            sample = agent_object.get_sample()
            print sample
        
        time.sleep(push_interval)


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

def _import_agents(agent_list):
    """
    Import the modules for the plugins specified in the
    config file, instantiate a class, and store it in
    a dict with it's name reference as the key
    """

    agent_object_dict = {}
    for agent in agent_list:
        # Import the module
        loaded_mod = __import__(agent['plugin'])
        class_name = _get_class_name(agent['plugin'])
        # Load class from imported module, instantiate an object,  and store it in dict
        agent_object_dict[agent['name']] = getattr(loaded_mod, class_name)(agent)
    # Will end up with something looking like:
    # { "mysqlagent1": <OBJ>, "systemagent1": <OBJ> }
    return agent_object_dict

def _get_class_name(mod_name):
    output = mod_name.title()
    return output


if __name__ == '__main__':
    main()

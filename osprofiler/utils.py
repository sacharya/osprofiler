import datetime
import socket
import yaml

epoch = datetime.datetime.utcfromtimestamp(0)
CONFIG_FILE = "/etc/osprofiler/osprofiler.conf"


def time_in_s():
    delta = datetime.datetime.now() - epoch
    return delta.total_seconds()


def time_in_ms():
    return int(time_in_s() * 1000.0)


def host_identifier():
    return "intel-cloud.%s" % socket.gethostname()


def number_or_string(val):
    try:
        return int(val)
    except ValueError:
        return val


def readConfig():
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

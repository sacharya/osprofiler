import datetime
import logging
import socket
import yaml

logger = logging.getLogger('osprofiler.%s' % __name__)
epoch = datetime.datetime.utcfromtimestamp(0)


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


def read_config(file_):
    """
    Read values from configuration file.

    @param file_ - String path of configuration file.
    @returns - Dictionary

    """
    try:
        with open(file_, 'r') as f:
            config = f.read()
        return yaml.load(config)
    except Exception:
        logger.exception("Unable to read configuration file %s" % file_)
        raise

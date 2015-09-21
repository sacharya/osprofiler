import logging
import logging.handlers
import os

DEFAULT_CONFIG = {
    'file': '/var/log/osprofiler/osprofiler',
    'level': 'info',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}


def init_logdir(logfile):
    """
    Creates the directories needed for logfile if they do not exist.

    @param logfile - String log file name/path

    """
    logdir, _ = os.path.split(logfile)
    if not os.path.exists(logdir):
        os.makedirs(logdir)


def get_logger(name='osprofiler'):
    """
    Returns a logger for logging.

    @param name - String name of the logger. osprofiler by default.
    @returns - logger

    """
    return logging.getLogger(name)

def load_config(filename, default=None):
    try :
        with open(filename, 'r') as f:
            diff = yaml.load(f)
            if diff is not None:
                return diff
    except IOError:
        return default

logging_conf_file = '/etc/osprofiler/logging.yaml'
logging_conf = load_config(logging_conf_file, default=DEFAULT_CONFIG)

# Get log path/file from config
logfile = logging_conf['file']
init_logdir(logfile)

# Get log level from config
loglevel = logging_conf['level']
loglevel = getattr(logging, loglevel.upper())

# Create log format from config
logformat = logging_conf['format']
logformatter = logging.Formatter(logformat)

# Create log handler
loghandler = logging.handlers.TimedRotatingFileHandler(
    logfile,
    when="midnight"
)
loghandler.setFormatter(logformatter)

import sys
consolehandler = logging.StreamHandler(sys.stdout)
# Set level and handler to root logger
logger = logging.getLogger()
logger.addHandler(loghandler)
logger.addHandler(consolehandler)
logger.setLevel(loglevel)

#TODO: Put each function call on it's own thread?

import os
import psutil
import time
import yaml

from cipsystem import CIPSystem

#GLOBAL CONSTANTS
CONFIG_FILE="/etc/cip/cip.conf"
SYSTEM_LOG_FILE="/var/log/cip/system.log"
RABBIT_LOG_FILE="/var/log/cip/rabbit.log"
MYSQL_LOG_FILE="/var/log/cip/mysql.log"

def main():
	"""Run the main application."""

        #Variables
        ##CIPSystem object to gathere system metrics
        systemReporter = CIPSystem()
	#rabbitReporter = 
	#mysqlReporter =

	#Reading the configuration file
        configDict = _readConfig()
	push_interval = configDict['push_interval']

	#Getting the PIDs of the processes we care about.
	#mysqlpid =
	#rabbitpid =

	while (True):
		_getSystemNetwork(systemReporter)
		_getSystemCPU(systemReporter)
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


def _getSystemNetwork(systemReporter):
	"""Get System Network Statistics."""
	print systemReporter.getNetworkIOStats()

def _getSystemMemory(systemReporter):
	"""Get System Memory Statistics."""
	print systemReporter.getMemoryStats()

def _getSystemCPU(systemReporter):
	"""Get System CPU Statistics."""
	print systemReporter.getCPUPercent()



if __name__ == '__main__':
	main()

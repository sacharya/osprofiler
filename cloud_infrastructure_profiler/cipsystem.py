import os
import psutils



class CIPSystem:
	"""A Class to retrieve information on system or process resource utilization.
	   Methods should return an object that can be sent to database backend. """
	#TODO: List methods of this class, and write a more detailed description.
	def __init__(self, metric, process="system"):
		self.metric = metric
		self.process = process


	def get_NetworkIOStats(self):
		psutil.net_io_counters()



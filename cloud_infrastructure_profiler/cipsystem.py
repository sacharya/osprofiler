import os
import psutil



class CIPSystem:
	"""A Class to retrieve information on system or process resource utilization.
	   Methods should return an object that can be sent to database backend. """
	#TODO: List methods of this class, and write a more detailed description.
	def __init__(self):
		self.data = "data"


	def get_NetworkIOStats(self):
		return psutil.net_io_counters()



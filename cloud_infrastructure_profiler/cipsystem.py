import os
import psutil


class Cipsystem:
    """
    A Class to retrieve information on system or process resource
    utilization. Methods should return an object that can be
    sent to database backend.
    """
    # TODO: List methods of this class, and write a more detailed description.
    def __init__(self, agent_config):
        self.agent_config = agent_config

    def get_network_stats(self):
        return psutil.net_io_counters()

    def get_cpu_stats(self):
        return psutil.cpu_percent()

    def get_memory_stats(self):
        return psutil.virtual_memory()

    def get_sample(self):
        # A list of metric objects. This is called a sample
        # The system plugin sample returns the system metrics 
        # defined in the config file.
        sample = { 
            "hostname": os.uname()[1],
            "agent_name": self.agent_config['name'],
            "metrics": list()
            }

        for metric in self.agent_config['metrics']:
            method_name = "get_" + metric + "_stats"
            metric_function_object = getattr(self, method_name)
            sample['metrics'].append(metric_function_object())
        return sample

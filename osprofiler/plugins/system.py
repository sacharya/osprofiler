import log
import os
import psutil
import pluginbase

logger = log.get_logger()

class System(pluginbase.PluginBase):
    """
    A Class to retrieve information on system or process resource
    utilization. Methods should return an object that can be
    sent to database backend.
    """
    # TODO: List methods of this class, and write a more detailed description.
    def __init__(self, *args, **kwargs):
        super(System, self).__init__(*args, **kwargs)

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
            "agent_name": self.config['name'],
            "metrics": list()
            }

        for metric in self.config['metrics']:
            method_name = "get_" + metric + "_stats"
            metric_function_object = getattr(self, method_name)
            sample['metrics'].append(metric_function_object())
        logger.info(sample)
        return sample

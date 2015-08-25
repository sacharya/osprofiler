import os
import psutil
import pluginbase

class System(pluginbase.PluginBase):
    """
    A Class to retrieve information on system or process resource
    utilization. Methods should return an object that can be
    sent to database backend.
    """
    # TODO: List methods of this class, and write a more detailed description.
    def __init__(self, *args, **kwargs):
        super(System, self).__init__(args, kwargs)
        #self.handlers = handlers

    def get_network_stats(self):
        return psutil.net_io_counters()

    def get_cpu_stats(self):
        return psutil.cpu_percent()

    def get_memory_stats(self):
        return psutil.virtual_memory()

    def get_sample(self):
        super(System, self).get_sample()
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
        print "Leaving " + self.__class__.__name__ + ".get_sample"
        return sample

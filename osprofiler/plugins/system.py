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
        network = {}
        for method in ['net_io_counters', 'net_if_stats', 'net_connections', 'net_if_stats']:
            mthd = getattr(psutil, method)
            obj = mthd()
            if type(obj) == 'dict':
                for key, val in obj.__dict__.items():
                    #print "%s: %s" % (key, val)
                    network['system.%s.%s' %(method, key)] = val
            elif type(obj) == 'list':
                #print "%s: %s" % (method, len(obj))
                network['system.%s.%s' %(method, key)] = len(obj)
        return network

    def get_cpu_stats(self):
        return psutil.cpu_percent()

    def get_memory_stats(self):
        memory = {}
        for key, value in psutil.virtual_memory().__dict__.items():
            memory["system.virtual_memory.%s" % key] = value
        for key, value in psutil.swap_memory().__dict__.items():
            memory["system.swap_memory.%s" % key] = value
        return memory

    def get_disk_stats(self):
        disk = {}
        for key, value in psutil.disk_usage("/").__dict__.items():
            disk["system.disk_usage.%s" % key] = value
        for key, value in psutil.disk_io_counters().__dict__.items():
             disk["system.disk_usage.%s" % key] = value
        for key, value in psutil.disk_partitions().__dict__.items():
            disk["system.disk_usage.%s" % key] = value
        return disk

    def get_sample(self):
        sample = { 
            "hostname": self.host_id,
            "agent_name": self.config['name'],
            "metrics": list()
            }
        memory = self.get_memory_stats()
        #cpu = self.get_cpu_stats()
        network = self.get_network_stats()
        #print type(network)
        mydict = memory.copy()
        #mydict.update(network)
        sample['metrics'].append(mydict)
        #logger.info(sample)
        return sample

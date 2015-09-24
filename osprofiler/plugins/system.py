import logging
import psutil
import pluginbase

logger = logging.getLogger('osprofiler.%s' % __name__)


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
        active_conns = [conn for conn in psutil.net_connections()
                        if conn.status == "ESTABLISHED"]
        network = {}
        network['system.net_connections.active'] = len(active_conns)
        for key, value in psutil.net_io_counters().__dict__.items():
            network["system.net_io_counters.%s" % key] = value
        return network

    def get_cpu_stats(self):
        cpu = {}
        for key, value in psutil.cpu_times_percent().__dict__.items():
            cpu["system.cpu_times.percent.%s" % key] = value
        cpu["system.cpu.percent"] = psutil.cpu_percent()
        return cpu

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
            disk["system.disk_io_counters.%s" % key] = value
        # for key, value in psutil.disk_partitions().__dict__.items():
        #    disk["system.disk_usage.%s" % key] = value
        return disk

    def get_sample(self):
        sample = {
            "hostname": self.host_id,
            "agent_name": self.config['name'],
            "metrics": list()
            }
        memory = self.get_memory_stats()
        cpu = self.get_cpu_stats()
        network = self.get_network_stats()
        disk = self.get_disk_stats()
        mydict = memory.copy()
        mydict.update(network)
        mydict.update(cpu)
        mydict.update(disk)
        sample['metrics'].append(mydict)
        logger.info(sample)
        return sample

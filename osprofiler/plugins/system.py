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
    unit_mapping = {
        'bytes_sent': 'bytes',
        'bytes_recv': 'bytes',
        'cpu.user': 'percent',
        'cpu.nice': 'percent',
        'cpu.system': 'percent',
        'cpu.idle': 'percent',
        'cpu.iowait': 'percent',
        'cpu.irq': 'percent',
        'cpu.softirq': 'percent',
        'cpu.steal': 'percent',
        'cpu.guest': 'percent',
        'cpu.guest_nice': 'percent',
        'virtual_memory.total': 'bytes',
        'virtual_memory.available': 'bytes',
        'virtual_memory.percent': 'percent',
        'virtual_memory.used': 'bytes',
        'virtual_memory.free': 'bytes',
        'swap_memory.total': 'bytes',
        'swap_memory.used': 'bytes',
        'swap_memory.free': 'bytes',
        'swap_memory.percent': 'percent'
    }

    # TODO: List methods of this class, and write a more detailed description.
    def __init__(self, **kwargs):
        super(System, self).__init__(**kwargs)

    def get_network_stats(self):
        active_conns = [conn for conn in psutil.net_connections()
                        if conn.status == "ESTABLISHED"]
        network = []
        network.append(
            self.metric_dict(
                self.metric_name('net_connections.active'),
                len(active_conns))
        )
        for key, value in psutil.net_io_counters().__dict__.items():
            network.append(self.metric_dict(
                self.metric_name("net_io_counters.%s" % key),
                value,
                self.unit_mapping.get(key)
            ))
        return network

    def get_cpu_stats(self):
        cpu = []
        cpu.append(
            self.metric_dict(self.metric_name("cpu.percent"),
                             psutil.cpu_percent(),
                             'percent')
        )
        for key, value in psutil.cpu_times_percent().__dict__.items():
            cpu.append(self.metric_dict(
                self.metric_name("cpu_times.percent.%s" % key),
                value,
                self.unit_mapping.get('cpu.%s' % key))
            )

        return cpu

    def get_memory_stats(self):
        memory = []
        for key, value in psutil.virtual_memory().__dict__.items():
            memory.append(self.metric_dict(
                self.metric_name("virtual_memory.%s" % key),
                value,
                self.unit_mapping.get('virtual_memory.%s' % key))
            )
        for key, value in psutil.swap_memory().__dict__.items():
            memory.append(self.metric_dict(
                self.metric_name("swap_memory.%s" % key),
                value,
                self.unit_mapping.get('swap_memory.%s' % key))
            )
        return memory

    def get_disk_stats(self):
        disk = []
        for key, value in psutil.disk_usage("/").__dict__.items():
            disk.append(self.metric_dict(
                self.metric_name("disk_usage./.%s" % key),
                value,
                self.unit_mapping.get('disk_usage.%s' % key))
            )
        for key, value in psutil.disk_io_counters().__dict__.items():
            disk.append(self.metric_dict(
                self.metric_name("disk_io_counters.%s" % key),
                value,
                self.unit_mapping.get('disk_usage.%s' % key))
            )
        return disk

    def get_sample(self):
        sample = {
            "hostname": self.host_id,
            "agent_name": self.config['name'],
            "metrics": list()
            }
        sample['metrics'].extend(self.get_memory_stats())
        sample['metrics'].extend(self.get_cpu_stats())
        sample['metrics'].extend(self.get_network_stats())
        sample['metrics'].extend(self.get_disk_stats())
        return sample

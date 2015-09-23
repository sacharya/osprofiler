import logging
import os
import psutil
import pluginbase

logger = logging.getLogger('osprofiler.%s' % __name__)


class Process(pluginbase.PluginBase):
    """
    A class to retrieve information on process resource
    utilization. This class is an agent of osprofiler and
    must follow the agent module template.
    """

    def __init__(self, *args, **kwargs):
        super(Process, self).__init__(*args, **kwargs)

    def _get_memory_stats(self, process):
        memory = {}
        name = process.name()
        memory_info = process.memory_info()
        memory_info_ex = process.memory_info_ex()
        memory["process.%s.memory_info.rss" % name] = memory_info.rss
        memory["process.%s.memory_info.vms" % name] = memory_info.vms
        memory["process.%s.memory_percent" % name] = process.memory_percent()
        memory["process.%s.memory_info_ex.rss" % name] = memory_info_ex.rss
        memory["process.%s.memory_info_ex.vms" % name] = memory_info_ex.vms
        return memory

    def _get_cpu_stats(self, process):
        cpu = {}
        name = process.name()
        cpu["process.%s.cpu_percent" % name] = process.cpu_percent()
        # cpu["process.%s.cpu_affinity" % name] = process.cpu_affinity()
        cpu["process.%s.cpu_times.user" % name] = process.cpu_times().user
        cpu["process.%s.cpu_times.system" % name] = process.cpu_times().system
        return cpu

    def _get_proc_obj(self, process_name):
        """
        This function returns the process' corresponding object.

        :param process_name: ```str``` The name of the service that we want
                                       to find the process object for.

        :returns: ```obj``` The process object that corresponds to the name.

        :returns: ```list of obj``` A list of process objects that
                                    correspond to the name.
        """

        proc_list = list()
        for proc in psutil.process_iter():
            try:
                # pinfo = proc.as_dict(attrs=['name', 'pid'])
                # if pinfo['name'] == process_name:
                proc_list.append(proc)
            except psutil.NoSuchProcess as ex:
                print str(ex)
                pass
        return proc_list

    def get_sample(self):
        sample = {
            "hostname": os.uname()[1],
            "agent_name": self.config['name'],
            "metrics": list()
            }

        proc_obj_list = self._get_proc_obj(self.config['process_name'])
        for proc_obj in proc_obj_list:
            if proc_obj is not None:
                try:
                    memory = self._get_memory_stats(proc_obj)
                    cpu = self._get_cpu_stats(proc_obj)
                    mydict = cpu.copy()
                    mydict.update(memory)
                    sample['metrics'].append(mydict)
                except psutil.NoSuchProcess as ex:
                    print str(ex)
                    pass
        # logger.info(sample)
        return sample

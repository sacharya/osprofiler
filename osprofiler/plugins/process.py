import log
import psutil
import os
import pluginbase

logger = log.get_logger()


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
        memory["process.%s.memory_info.rss" % process.name()] = process.memory_info().rss
        memory["process.%s.memory_info.vms" % process.name()] = process.memory_info().vms
        memory["process.%s.memory_percent" % process.name()] = process.memory_percent()
        memory["process.%s.memory_info_ex.rss" % process.name()] = process.memory_info().rss
        memory["process.%s.memory_info_ex.vms" % process.name()] = process.memory_info_ex().vms         
        return memory

    def _get_cpu_stats(self, process):
        cpu = {}
        cpu["process.%s.cpu_percent" % process.name()] = process.cpu_percent()
        #cpu["process.%s.cpu_affinity" % process.name()] = process.cpu_affinity()
        cpu["process.%s.cpu_times.user" % process.name()] = process.cpu_times().user
        cpu["process.%s.cpu_times.system" % process.name()] = process.cpu_times().system
        return cpu

    def _get_proc_obj(self, process_name):
        """
        This function returns the process' corresponding object.
        
        :param process_name: ```str``` The name of the service that we want
                                       to find the process object for.

        :returns: ```obj``` The process object that corresponds to the name.

        :returns: ```list of obj``` A list of process objects that correspond to the name.
        """

        proc_list = list()
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['name','pid'])
                #if pinfo['name'] == process_name:
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
                try :
                    memory = self._get_memory_stats(proc_obj)
                    cpu = self._get_cpu_stats(proc_obj)
                    mydict = cpu.copy()
                    mydict.update(memory)
                    sample['metrics'].append(mydict)
                except psutil.NoSuchProcess as ex:
                    print str(ex)
                    pass
        #logger.info(sample)
        #import pprint
        #pprint.pprint(sample)
        return sample

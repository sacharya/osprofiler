# Get process information

import psutil
import os


class Process:
    """
    A class to retrieve information on process resource
    utilization. This class is an agent of osprofiler and
    must follow the agent module template.
    """

    def __init__(self, agent_config):
        self.agent_config = agent_config


    def _get_memory_stats(self, proc_obj):
        return proc_obj.memory_info()

    def _get_cpu_stats(self, proc_obj):
        return proc_obj.cpu_info()

    def _get_network_stats(self, proc_obj):
        return proc_obj.network_info()

    def _get_proc_obj(self, process_name):
        """
        This function returns the process' corresponding object.
        
        :param process_name: ```str``` The name of the service that we want
                                       to find the process object for.

        :returns: ```obj``` The process object that corresponds to the name.
        """
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['name','pid'])
                if pinfo['name'] == process_name:
                    return proc
            except psutil.NoSuchProcess as ex:
                print str(ex)
                pass
        return None

    def get_sample(self):
        print self.__class__.__name__ + ".get_sample"
        sample = {
            "hostname": os.uname()[1],
            "agent_name": self.agent_config['name'],
            "metrics": list()
            }

        proc_obj = self._get_proc_obj(self.agent_config['process_name'])
        
        for metric in self.agent_config['metrics']:
            method_name = "_get_" + metric + "_stats"
            metric_function_object = getattr(self, method_name)
            if proc_obj is not None:
                sample['metrics'].append(metric_function_object(proc_obj))

        return sample

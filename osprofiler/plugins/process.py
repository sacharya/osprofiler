# Get process information

import psutil
import os
import pluginbase

class Process(pluginbase.PluginBase):
    """
    A class to retrieve information on process resource
    utilization. This class is an agent of osprofiler and
    must follow the agent module template.
    """

    def __init__(self, *args, **kwargs):
        super(Process, self).__init__(args, kwargs)
        #self.handlers = handlers

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

        :returns: ```list of obj``` A list of process objects that correspond to the name.
        """

        proc_obj_list = list()
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['name','pid'])
                if pinfo['name'] == process_name:
                    proc_obj_list.append(proc)
            except psutil.NoSuchProcess as ex:
                print str(ex)
                pass
        return proc_obj_list

    def get_sample(self):
        super(Process, self).get_sample()
        sample = {
            "hostname": os.uname()[1],
            "agent_name": self.config['name'],
            "metrics": list()
            }

        proc_obj_list = self._get_proc_obj(self.config['process_name'])
        
        for metric in self.config['metrics']:
            method_name = "_get_" + metric + "_stats"
            metric_function_object = getattr(self, method_name)
            for proc_obj in proc_obj_list:
                if proc_obj is not None:
                    pid_metrics = {"pid": int(), "metric_values": list()}
                    pid_metrics['pid'] = proc_obj.pid
                    pid_metrics['metric_values'].append(metric_function_object(proc_obj))
                    sample['metrics'].append(pid_metrics)
        print "Leaving " + self.__class__.__name__ + ".get_sample"
        return sample

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

    def __init__(self, **kwargs):
        super(Process, self).__init__(**kwargs)

    def metric_name(self, suffix, process):
        """
        Creates a dictionary key for a process with a suffix.
        Will be in the format: {process_name}.{pid}.{suffix}

        @param suffix - String
        @param process - Process object
        @returns - String

        """
        suffix = "{process_name}.{pid}.{suffix}".format(
            process_name=process.name(),
            pid=process.pid,
            suffix=suffix
        )
        return super(Process, self).metric_name(suffix)

    def _get_memory_stats(self, process):
        memory_info = process.memory_info()
        memory_info_ex = process.memory_info_ex()
        percent = process.memory_percent()
        return [
            self.metric_dict(self.metric_name('memory_info.rss', process),
                             memory_info.rss,
                             'bytes'),
            self.metric_dict(self.metric_name('memory_info.vms', process),
                             memory_info.vms,
                             'bytes'),
            self.metric_dict(self.metric_name('memory_percent', process),
                             percent,
                             'percent'),
            self.metric_dict(self.metric_name('memory_info_ex.rss', process),
                             memory_info_ex.rss,
                             'bytes'),
            self.metric_dict(self.metric_name('memory_info_ex.vms', process),
                             memory_info_ex.vms,
                             'bytes')
        ]

    def _get_cpu_stats(self, process):
        cpu_times = process.cpu_times()
        return [
            self.metric_dict(
                self.metric_name('cpu_percent', process),
                process.cpu_percent(),
                'percent'
            ),
            self.metric_dict(
                self.metric_name('cpu_times.user', process),
                cpu_times.user,
                'seconds'
            ),
            self.metric_dict(
                self.metric_name('cpu_times.system', process),
                cpu_times.system,
                'seconds'
            )
        ]

    def _should_get_metric(self, metric):
        """
        Returns whether or not to grab a metric like cpu or memory

        @param metric - String name of a metric: 'cpu', 'memory'
        @return bool
        """
        metrics = self.config.get('metrics', [])
        if not metrics:
            return True
        return metric in metrics

    def _get_proc_obj(self):
        """
        This function returns the process' corresponding object.

        :returns: ```obj``` The process object that corresponds to the name.

        :returns: ```list of obj``` A list of process objects that
                                    correspond to the name.
        """
        filters = self.config.get('filters')
        proc_list = list()

        if filters:
            for proc in psutil.process_iter():
                try:
                    for f in filters:
                        if f in proc.name():
                            proc_list.append(proc)
                            break
                except psutil.NoSuchProcess:
                    logger.exception("Error occurred obtaining process.")
                pass
        else:
            for proc in psutil.process_iter():
                try:
                    proc_list.append(proc)
                except psutil.NoSuchProcess:
                    logger.exception("Error occurred obtaining process.")
                    pass
        return proc_list

    def get_sample(self):
        sample = {
            "hostname": os.uname()[1],
            "agent_name": self.config.get('name', 'process'),
            "metrics": list()
            }

        proc_obj_list = self._get_proc_obj()
        for proc_obj in proc_obj_list:
            if proc_obj is not None:
                try:
                    if self._should_get_metric('memory'):
                        sample['metrics'].extend(
                            self._get_memory_stats(proc_obj)
                        )
                    if self._should_get_metric('cpu'):
                        sample['metrics'].extend(
                            self._get_cpu_stats(proc_obj)
                        )
                except psutil.NoSuchProcess:
                    logger.exception("Error sampling process information")
                    pass
        return sample

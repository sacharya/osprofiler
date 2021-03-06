import mock
import socket
import unittest

import base
from osprofiler.plugins.process import Process


class FakeProcess(object):

    def __init__(self, name, pid=1):
        self._name = name
        self.pid = pid

    def name(self):
        return self._name

    def memory_percent(self):
        return 1

    def memory_info(self):
        class FakeMemoryInfo(object):
            def __init__(self):
                self.rss = 2
                self.vms = 3
        return FakeMemoryInfo()

    def memory_info_ex(self):
        class FakeMemoryInfo(object):
            def __init__(self):
                self.rss = 4
                self.vms = 5
        return FakeMemoryInfo()

    def cpu_percent(self):
        return 11

    def cpu_times(self):
        class FakeCpuTimes(object):
            def __init__(self):
                self.user = 12
                self.system = 13
        return FakeCpuTimes()

fake_names = ["alpha", "bravo", "charlie", "delta", "echo"]


def mock_process_iter():
    """
    Returns an iterable list of fake processes.

    """
    for i, name in enumerate(fake_names):
        yield FakeProcess(name, i + 1)


class TestPluginProcess(unittest.TestCase):
    """
    Tests for the process plugin

    """
    @mock.patch('socket.gethostname', return_value='testhost')
    def test_memory_stats(self, mocked_function):
        """
        Test memory stats

        """
        plugin = Process(config={'name': 'process'})
        fake_process = FakeProcess('test')
        expected = [
            {
                'name': 'testhost.process.test.1.memory_percent',
                'value': 1,
                'units': 'percent'
            },
            {
                'name': 'testhost.process.test.1.memory_info.rss',
                'value': 2,
                'units': 'bytes'
            },
            {
                'name': 'testhost.process.test.1.memory_info.vms',
                'value': 3,
                'units': 'bytes'
            },
            {
                'name': 'testhost.process.test.1.memory_info_ex.rss',
                'value': 4,
                'units': 'bytes'
            },
            {
                'name': 'testhost.process.test.1.memory_info_ex.vms',
                'value': 5,
                'units': 'bytes'
            }
        ]
        for metric in plugin._get_memory_stats(fake_process):
            for e_metric in expected:
                if metric['name'] == e_metric['name']:
                    self.assertEquals(metric['value'], e_metric['value'])
                    self.assertEquals(metric['units'], e_metric['units'])
                    break
            else:
                self.fail("Metric %s not in expected" % metric['name'])

    @mock.patch('socket.gethostname', return_value='testhost')
    def test_cpu_stats(self, mocked_function):
        """
        Test CPU stats

        """
        plugin = Process(config={'name': 'process'})
        fake_process = FakeProcess('test')
        expected = [
            {
                'name': 'testhost.process.test.1.cpu_percent',
                'value': 11,
                'units': 'percent'
            },
            {
                'name': 'testhost.process.test.1.cpu_times.user',
                'value': 12,
                'units': 'seconds'
            },
            {
                'name': 'testhost.process.test.1.cpu_times.system',
                'value': 13,
                'units': 'seconds'
            }
        ]
        for metric in plugin._get_cpu_stats(fake_process):
            for e_metric in expected:
                if metric['name'] == e_metric['name']:
                    self.assertEquals(metric['value'], e_metric['value'])
                    self.assertEquals(metric['units'], e_metric['units'])
                    break
            else:
                self.fail("Metric %s not in expected" % metric['name'])

    @mock.patch('psutil.process_iter', side_effect=mock_process_iter)
    def test_metrics(self, mocked_function):
        """
        Tests the metrics section of the configuration

        """
        # Cpu only
        config = {'metrics': ['cpu']}
        plugin = Process(config=config)
        plugin._get_cpu_stats = mock.Mock(return_value={})
        plugin._get_memory_stats = mock.Mock(return_value={})
        self.assertTrue(plugin._should_get_metric('cpu'))
        self.assertFalse(plugin._should_get_metric('memory'))
        plugin.get_sample()
        self.assertTrue(plugin._get_cpu_stats.called)
        self.assertFalse(plugin._get_memory_stats.called)

        # Memory only
        config = {'metrics': ['memory']}
        plugin = Process(config=config)
        plugin._get_cpu_stats = mock.Mock(return_value={})
        plugin._get_memory_stats = mock.Mock(return_value={})
        self.assertFalse(plugin._should_get_metric('cpu'))
        self.assertTrue(plugin._should_get_metric('memory'))
        plugin.get_sample()
        self.assertFalse(plugin._get_cpu_stats.called)
        self.assertTrue(plugin._get_memory_stats.called)

        # Memory and cpu explicit
        config = {'metrics': ['memory', 'cpu']}
        plugin = Process(config=config)
        plugin._get_cpu_stats = mock.Mock(return_value={})
        plugin._get_memory_stats = mock.Mock(return_value={})
        self.assertTrue(plugin._should_get_metric('cpu'))
        self.assertTrue(plugin._should_get_metric('memory'))
        plugin.get_sample()
        self.assertTrue(plugin._get_cpu_stats.called)
        self.assertTrue(plugin._get_memory_stats.called)

        # Memory and cpu implicit
        config = {'metrics': []}
        plugin = Process(config=config)
        plugin._get_cpu_stats = mock.Mock(return_value={})
        plugin._get_memory_stats = mock.Mock(return_value={})
        self.assertTrue(plugin._should_get_metric('cpu'))
        self.assertTrue(plugin._should_get_metric('memory'))
        plugin.get_sample()
        self.assertTrue(plugin._get_cpu_stats.called)
        self.assertTrue(plugin._get_memory_stats.called)

    @mock.patch('psutil.process_iter', side_effect=mock_process_iter)
    def test_proc_names(self, mocked_function):
        """
        Tests that configuration of allowable process names is used
        to filter out unwanted processes

        """
        # Test that providing no list returns all procs
        config = {'filters': []}
        plugin = Process(config=config)
        for proc in plugin._get_proc_obj():
            self.assertTrue(proc.name() in fake_names)

        # Test that exact matches are returned
        expected = ['alpha', 'echo']
        config = {'filters': expected}
        plugin = Process(config=config)
        for proc in plugin ._get_proc_obj():
            self.assertTrue(proc.name() in expected)

        # Test that partial matches are returned.
        expected = ['alpha', 'echo']
        config = {'filters': ['al', 'cho']}
        plugin = Process(config=config)
        for proc in plugin._get_proc_obj():
            self.assertTrue(proc.name() in expected)

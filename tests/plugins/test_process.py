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
        memory_stats = plugin._get_memory_stats(fake_process)
        self.assertTrue(isinstance(memory_stats, dict))
        expected = {
            'testhost.process.test.1.memory_percent': 1,
            'testhost.process.test.1.memory_info.rss': 2,
            'testhost.process.test.1.memory_info.vms': 3,
            'testhost.process.test.1.memory_info_ex.rss': 4,
            'testhost.process.test.1.memory_info_ex.vms': 5
        }
        for key, value in expected.iteritems():
            self.assertTrue(key in memory_stats)
            self.assertEquals(memory_stats[key], value)

    @mock.patch('socket.gethostname', return_value='testhost')
    def test_cpu_stats(self, mocked_function):
        """
        Test CPU stats

        """
        plugin = Process(config={'name': 'process'})
        fake_process = FakeProcess('test')
        cpu_stats = plugin._get_cpu_stats(fake_process)
        self.assertTrue(isinstance(cpu_stats, dict))
        expected = {
            'testhost.process.test.1.cpu_percent': 11,
            'testhost.process.test.1.cpu_times.user': 12,
            'testhost.process.test.1.cpu_times.system': 13
        }
        for key, value in expected.iteritems():
            self.assertTrue(key in cpu_stats)
            self.assertEquals(cpu_stats[key], value)

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

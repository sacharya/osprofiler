import mock
import socket
import unittest

from collections import OrderedDict

import base
from osprofiler.plugins.system import System, psutil


class FakeConnection():
    def __init__(self, established=True):
        if established:
            self.status = 'ESTABLISHED'
        else:
            self.status = 'nonsense'


def fake_net_connections():
    for i in xrange(5):
        yield FakeConnection(established=True)
    for i in xrange(10):
        yield FakeConnection(established=False)


def fake_net_io_counters():
    class FakeCounters(object):
        def __init__(self):
            self.__dict__ = OrderedDict([
                ('bytes_sent', 1),
                ('bytes_recv', 2),
                ('packets_sent', 3),
                ('packets_recv', 4),
                ('errin', 5),
                ('errout', 6),
                ('dropin', 7),
                ('dropout', 8)
            ])
    return FakeCounters()


def fake_cpu_times_percent():
    class FakePercents():
        def __init__(self):
            self.__dict__ = OrderedDict([
                ('user', 1),
                ('nice', 2),
                ('system', 3),
                ('idle', 4),
                ('iowait', 5),
                ('irq', 6),
                ('softirq', 7),
                ('steal', 8),
                ('guest', 9),
                ('guest_nice', 10)
            ])
    return FakePercents()


def fake_virtual_memory():
    class FakeMemory():
        def __init__(self):
            self.__dict__ = OrderedDict([
                ('total', 1),
                ('available', 2),
                ('percent', 3),
                ('used', 4),
                ('free', 5),
                ('active', 6),
                ('inactive', 7),
                ('buffers', 8),
                ('cached', 9)
            ])
    return FakeMemory()


def fake_swap_memory():
    class FakeMemory():
        def __init__(self):
            self.__dict__ = OrderedDict([
                ('total', 1),
                ('used', 2),
                ('free', 3),
                ('percent', 4),
                ('sin', 5),
                ('sout', 6)
            ])
    return FakeMemory()


def fake_disk_usage(disk):
    class FakeUsage():
        def __init__(self):
            self.__dict__ = OrderedDict([
                ('total', 1),
                ('used', 2),
                ('free', 3),
                ('percent', 4)
            ])
    return FakeUsage()


def fake_disk_counters():
    class FakeCounters():
        def __init__(self):
            self.__dict__ = OrderedDict([
                ('read_count', 1),
                ('write_count', 2),
                ('read_bytes', 3),
                ('write_bytes', 4),
                ('read_time', 5),
                ('write_time', 6)
            ])
    return FakeCounters()


class TestPluginSystem(unittest.TestCase):
    """
    Tests for the system plugin

    """
    @mock.patch('socket.gethostname', return_value='testhost')
    @mock.patch('psutil.net_connections', side_effect=fake_net_connections)
    @mock.patch('psutil.net_io_counters', side_effect=fake_net_io_counters)
    def test_network_stats(self, *mocked):
        """
        Test network stats

        """
        plugin = System(config={'name': 'system'})
        expected = {
            'testhost.system.net_connections.active': 5,
            'testhost.system.net_io_counters.bytes_sent': 1,
            'testhost.system.net_io_counters.bytes_recv': 2,
            'testhost.system.net_io_counters.packets_sent': 3,
            'testhost.system.net_io_counters.packets_recv': 4,
            'testhost.system.net_io_counters.errin': 5,
            'testhost.system.net_io_counters.errout': 6,
            'testhost.system.net_io_counters.dropin': 7,
            'testhost.system.net_io_counters.dropout': 8
        }
        stats = plugin.get_network_stats()
        for key, value in stats.iteritems():
            self.assertTrue(key in expected)
            self.assertEquals(value, expected[key])

    @mock.patch('socket.gethostname', return_value='testhost')
    @mock.patch('psutil.cpu_times_percent', side_effect=fake_cpu_times_percent)
    @mock.patch('psutil.cpu_percent', return_value=100)
    def test_cpu_stats(self, *mocked):
        plugin = System(config={'name': 'system'})
        expected = {
            'testhost.system.cpu_times.percent.user': 1,
            'testhost.system.cpu_times.percent.nice': 2,
            'testhost.system.cpu_times.percent.system': 3,
            'testhost.system.cpu_times.percent.idle': 4,
            'testhost.system.cpu_times.percent.iowait': 5,
            'testhost.system.cpu_times.percent.irq': 6,
            'testhost.system.cpu_times.percent.softirq': 7,
            'testhost.system.cpu_times.percent.steal': 8,
            'testhost.system.cpu_times.percent.guest': 9,
            'testhost.system.cpu_times.percent.guest_nice': 10,
            'testhost.system.cpu.percent': 100
        }
        stats = plugin.get_cpu_stats()
        for key, value in stats.iteritems():
            self.assertTrue(key in expected)
            self.assertEquals(value, expected[key])

    @mock.patch('socket.gethostname', return_value='testhost')
    @mock.patch('psutil.virtual_memory', side_effect=fake_virtual_memory)
    @mock.patch('psutil.swap_memory', side_effect=fake_swap_memory)
    def test_memory_stats(self, *mocked):
        plugin = System(config={'name': 'system'})
        expected = {
            'testhost.system.virtual_memory.total': 1,
            'testhost.system.virtual_memory.available': 2,
            'testhost.system.virtual_memory.percent': 3,
            'testhost.system.virtual_memory.used': 4,
            'testhost.system.virtual_memory.free': 5,
            'testhost.system.virtual_memory.active': 6,
            'testhost.system.virtual_memory.inactive': 7,
            'testhost.system.virtual_memory.buffers': 8,
            'testhost.system.virtual_memory.cached': 9,
            'testhost.system.swap_memory.total': 1,
            'testhost.system.swap_memory.used': 2,
            'testhost.system.swap_memory.free': 3,
            'testhost.system.swap_memory.percent': 4,
            'testhost.system.swap_memory.sin': 5,
            'testhost.system.swap_memory.sout': 6
        }
        stats = plugin.get_memory_stats()
        for key, value in stats.iteritems():
            self.assertTrue(key in expected)
            self.assertEquals(value, expected[key])

    @mock.patch('socket.gethostname', return_value='testhost')
    @mock.patch('psutil.disk_usage', side_effect=fake_disk_usage)
    @mock.patch('psutil.disk_io_counters', side_effect=fake_disk_counters)
    def test_disk_stats(self, *mocked):
        plugin = System(config={'name': 'system'})
        expected = {
            'testhost.system.disk_usage./.total': 1,
            'testhost.system.disk_usage./.used': 2,
            'testhost.system.disk_usage./.free': 3,
            'testhost.system.disk_usage./.percent': 4,
            'testhost.system.disk_io_counters.read_count': 1,
            'testhost.system.disk_io_counters.write_count': 2,
            'testhost.system.disk_io_counters.read_bytes': 3,
            'testhost.system.disk_io_counters.write_bytes': 4,
            'testhost.system.disk_io_counters.read_time': 5,
            'testhost.system.disk_io_counters.write_time': 6
        }
        stats = plugin.get_disk_stats()
        for key, value in stats.iteritems():
            self.assertTrue(key in expected)
            self.assertEquals(value, expected[key])

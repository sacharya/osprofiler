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
        expected = [
            {
                'name': 'testhost.system.net_connections.active',
                'value': 5
            },
            {
                'name': 'testhost.system.net_io_counters.bytes_sent',
                'value': 1,
                'units': 'bytes'
            },
            {
                'name': 'testhost.system.net_io_counters.bytes_recv',
                'value': 2,
                'units': 'bytes'
            },
            {
                'name': 'testhost.system.net_io_counters.packets_sent',
                'value': 3,
            },
            {
                'name': 'testhost.system.net_io_counters.packets_recv',
                'value': 4
            },
            {
                'name': 'testhost.system.net_io_counters.errin',
                'value': 5,
            },
            {
                'name': 'testhost.system.net_io_counters.errout',
                'value': 6,
            },
            {
                'name': 'testhost.system.net_io_counters.dropin',
                'value': 7,
            },
            {
                'name': 'testhost.system.net_io_counters.dropout',
                'value': 8
            }
        ]
        for metric in plugin.get_network_stats():
            for e_metric in expected:
                if metric['name'] == e_metric['name']:
                    self.assertEquals(metric['value'], e_metric['value'])
                    self.assertEquals(metric.get('units'),
                                      e_metric.get('units'))
                    break
            else:
                self.fail("Metric %s not in expected" % metric['name'])

    @mock.patch('socket.gethostname', return_value='testhost')
    @mock.patch('psutil.cpu_times_percent', side_effect=fake_cpu_times_percent)
    @mock.patch('psutil.cpu_percent', return_value=100)
    def test_cpu_stats(self, *mocked):
        plugin = System(config={'name': 'system'})
        expected = [
            {
                'name': 'testhost.system.cpu_times.percent.user',
                'value': 1,
                'units': 'percent'
            },
            {
                'name': 'testhost.system.cpu_times.percent.nice',
                'value': 2,
                'units': 'percent'
            },
            {
                'name': 'testhost.system.cpu_times.percent.system',
                'value': 3,
                'units': 'percent'
            },
            {
                'name': 'testhost.system.cpu_times.percent.idle',
                'value': 4,
                'units': 'percent'
            },
            {
                'name': 'testhost.system.cpu_times.percent.iowait',
                'value': 5,
                'units': 'percent'
            },
            {
                'name': 'testhost.system.cpu_times.percent.irq',
                'value': 6,
                'units': 'percent'
            },
            {
                'name': 'testhost.system.cpu_times.percent.softirq',
                'value': 7,
                'units': 'percent'
            },
            {
                'name': 'testhost.system.cpu_times.percent.steal',
                'value': 8,
                'units': 'percent'
            },
            {
                'name': 'testhost.system.cpu_times.percent.guest',
                'value': 9,
                'units': 'percent'
            },
            {
                'name': 'testhost.system.cpu_times.percent.guest_nice',
                'value': 10,
                'units': 'percent'
            },
            {
                'name': 'testhost.system.cpu.percent',
                'value': 100,
                'units': 'percent'
            }
        ]
        for metric in plugin.get_cpu_stats():
            for e_metric in expected:
                if metric['name'] == e_metric['name']:
                    self.assertEquals(metric['value'], e_metric['value'])
                    self.assertEquals(metric.get('units'),
                                      e_metric.get('units'))
                    break
            else:
                self.fail("Metric %s not in expected" % metric['name'])

    @mock.patch('socket.gethostname', return_value='testhost')
    @mock.patch('psutil.virtual_memory', side_effect=fake_virtual_memory)
    @mock.patch('psutil.swap_memory', side_effect=fake_swap_memory)
    def test_memory_stats(self, *mocked):
        plugin = System(config={'name': 'system'})
        expected = [
            {
                'name': 'testhost.system.virtual_memory.total',
                'value': 1,
                'units': 'bytes'
            },
            {
                'name': 'testhost.system.virtual_memory.available',
                'value': 2,
                'units': 'bytes'
            },
            {
                'name': 'testhost.system.virtual_memory.percent',
                'value': 3,
                'units': 'percent'
            },
            {
                'name': 'testhost.system.virtual_memory.used',
                'value': 4,
                'units': 'bytes'
            },
            {
                'name': 'testhost.system.virtual_memory.free',
                'value': 5,
                'units': 'bytes'
            },
            {
                'name': 'testhost.system.virtual_memory.active',
                'value': 6
            },
            {
                'name': 'testhost.system.virtual_memory.inactive',
                'value': 7
            },
            {
                'name': 'testhost.system.virtual_memory.buffers',
                'value': 8
            },
            {
                'name': 'testhost.system.virtual_memory.cached',
                'value': 9
            },
            {
                'name': 'testhost.system.swap_memory.total',
                'value': 1,
                'units': 'bytes'
            },
            {
                'name': 'testhost.system.swap_memory.used',
                'value': 2,
                'units': 'bytes'
            },
            {
                'name': 'testhost.system.swap_memory.free',
                'value': 3,
                'units': 'bytes'
            },
            {
                'name': 'testhost.system.swap_memory.percent',
                'value': 4,
                'units': 'percent'
            },
            {
                'name': 'testhost.system.swap_memory.sin',
                'value': 5
            },
            {
                'name': 'testhost.system.swap_memory.sout',
                'value': 6
            }
        ]
        for metric in plugin.get_memory_stats():
            for e_metric in expected:
                if metric['name'] == e_metric['name']:
                    self.assertEquals(metric['value'], e_metric['value'])
                    self.assertEquals(metric.get('units'),
                                      e_metric.get('units'))
                    break
            else:
                self.fail("Metric %s not in expected" % metric['name'])

    @mock.patch('socket.gethostname', return_value='testhost')
    @mock.patch('psutil.disk_usage', side_effect=fake_disk_usage)
    @mock.patch('psutil.disk_io_counters', side_effect=fake_disk_counters)
    def test_disk_stats(self, *mocked):
        plugin = System(config={'name': 'system'})
        expected = [
            {
                'name': 'testhost.system.disk_usage./.total',
                'value': 1
            },
            {
                'name': 'testhost.system.disk_usage./.used',
                'value': 2
            },
            {
                'name': 'testhost.system.disk_usage./.free',
                'value': 3
            },
            {
                'name': 'testhost.system.disk_usage./.percent',
                'value': 4
            },
            {
                'name': 'testhost.system.disk_io_counters.read_count',
                'value': 1
            },
            {
                'name': 'testhost.system.disk_io_counters.write_count',
                'value': 2
            },
            {
                'name': 'testhost.system.disk_io_counters.read_bytes',
                'value': 3
            },
            {
                'name': 'testhost.system.disk_io_counters.write_bytes',
                'value': 4
            },
            {
                'name': 'testhost.system.disk_io_counters.read_time',
                'value': 5
            },
            {
                'name': 'testhost.system.disk_io_counters.write_time',
                'value': 6
            }
        ]
        for metric in plugin.get_disk_stats():
            for e_metric in expected:
                if metric['name'] == e_metric['name']:
                    self.assertEquals(metric['value'], e_metric['value'])
                    self.assertEquals(metric.get('units'),
                                      e_metric.get('units'))
                    break
            else:
                self.fail("Metric %s not in expected" % metric['name'])

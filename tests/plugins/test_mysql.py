import mock
import socket
import unittest

import base
from osprofiler.plugins.mysql import Mysql


class TestMysqlProcess(unittest.TestCase):
    """
    Tests for the mysql plugin

    """
    sample_output = "\n".join([
        "Variable_name\tValue",
        "Queries\t1",
        "Threads_cached\t2",
        "Threads_connected\t3",
        "Threads_created\t4",
        "Threads_running\t5"
    ])

    @mock.patch('socket.gethostname', return_value='testhost')
    def test_metric_names(self, mocked_function):
        """
        Tests that correct metric names are generated.

        """
        plugin = Mysql(config={'name': 'mysql'})
        mock_check = mock.Mock(return_value=(0, self.sample_output, ""))
        plugin.galera_status_check = mock_check
        expected = [
            {
                'name': 'testhost.mysql.Queries',
                'value': 1
            },
            {
                'name': 'testhost.mysql.Threads_cached',
                'value': 2
            },
            {
                'name': 'testhost.mysql.Threads_connected',
                'value': 3
            },
            {
                'name': 'testhost.mysql.Threads_created',
                'value': 4,
            },
            {
                'name': 'testhost.mysql.Threads_running',
                'value': 5,
            }
        ]
        for metric in plugin.get_sample()['metrics']:
            for e_metric in expected:
                if metric['name'] == e_metric['name']:
                    self.assertEquals(metric['value'], e_metric['value'])
                    self.assertEquals(metric.get('units'),
                                      e_metric.get('units'))
                    break
            else:
                self.fail("Metric %s not in expected" % metric['name'])

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

        sample = plugin.get_sample()

        expected = {
            'testhost.mysql.Queries': 1,
            'testhost.mysql.Threads_cached': 2,
            'testhost.mysql.Threads_connected': 3,
            'testhost.mysql.Threads_created': 4,
            'testhost.mysql.Threads_running': 5,
        }
        for metric_dict in sample.get('metrics', []):
            for key, value in metric_dict.iteritems():
                self.assertTrue(key in expected)
                self.assertEquals(value, expected[key])

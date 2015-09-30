import mock
import socket
import unittest

import base
from osprofiler.plugins.pluginbase import PluginBase, PluginException


class TestException(Exception):
    pass


def raise_test_exception(val1):
    raise TestException()


class TestPluginBase(unittest.TestCase):
    """
    Tests the plugin base class

    """

    def test_get_sample_not_implemented(self):
        """
        Tests that the get sample method raises a PluginException
        if the subclass has not implemented  the get_sample method.

        """
        plugin = PluginBase()
        self.assertRaises(PluginException, plugin.get_sample)

    def test_no_config(self):
        """
        Tests plugin base with no config provided.

        """
        plugin = PluginBase()
        self.assertTrue(isinstance(plugin.config, dict))
        self.assertTrue(isinstance(plugin.handlers, list))

    @mock.patch('time.sleep', side_effect=raise_test_exception)
    def test_sleep(self, sleep_function):
        """
        Tests a sleep with a push interval is called in the long running
        loop. TestException should break the loop.

        """
        default_sample_interval = 5
        plugin = PluginBase()
        self.assertRaises(TestException, plugin.execute)
        sleep_function.assert_called_with(default_sample_interval)

        config = {'sample_interval': 100}
        plugin = PluginBase(config=config)
        self.assertRaises(TestException, plugin.execute)
        sleep_function.assert_called_with(config['sample_interval'])

    @mock.patch('time.sleep', side_effect=raise_test_exception)
    def test_get_sample_and_handler(self, sleep_function):
        """
        Tests that a subclasses get_sample method is called and that
        the value returned from get_sample is passed to a handler.

        """
        class TestPlugin(PluginBase):
            pass

        handler = mock.Mock()
        plugin = TestPlugin(handlers=[handler])
        plugin.get_sample = mock.Mock()
        plugin.get_sample.return_value = 10

        self.assertRaises(TestException, plugin.execute)
        assert plugin.get_sample.called
        handler.handle.assert_called_with(10)

    @mock.patch('socket.gethostname', return_value='testhost')
    def test_metric_name(self, mocked_function):
        """
        Tests metric name method with default prefix and non default

        """
        # Test defaults - No prefix and name should default to 'agent'
        plugin = PluginBase()
        expected = "testhost.agent.suffix"
        name = plugin.metric_name('suffix')
        self.assertEquals(name, expected)

        # Test prefix - no name
        plugin = PluginBase(config={'prefix': 'prefix'})
        expected = "prefix.testhost.agent.suffix"
        self.assertEquals(plugin.metric_name('suffix'), expected)

        # Test name - no prefix
        plugin = PluginBase(config={'name': 'testagent'})
        expected = "testhost.testagent.suffix"
        self.assertEquals(plugin.metric_name('suffix'), expected)

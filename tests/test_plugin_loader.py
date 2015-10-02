import base
import mock
import unittest

from osprofiler.plugin_loader import PluginLoader


def load_object(params, handlers=None):
    """
    Returns string from params

    """
    return "%s:%s" % (params['name'], params['plugin'])


class TestPluginLoader(unittest.TestCase):
    """
    Tests for the plugin loader

    """
    def test_init(self):
        """
        Tests that an instance is initialized.

        """
        config = {
            'agents': 1,
            'backend': 2
        }
        loader = PluginLoader(config)
        self.assertTrue(isinstance(loader.config, dict))
        self.assertEquals(loader.agent_list, config['agents'])
        self.assertEquals(loader.backend_list, config['backend'])

    def test_load_plugins(self):
        """
        Tests that backends and agents are loaded correctly.

        """
        config = {
            'agents': [
                {
                    'name': 'agent1',
                    'plugin': 'plugins.plugin1'
                },
                {
                    'name': 'agent2',
                    'plugin': 'plugins.plugin2'
                }
            ],
            'backend': [
                {
                    'name': 'backend1',
                    'plugin': 'plugins.plugin3'
                },
                {
                    'name': 'backend2',
                    'plugin': 'plugins.plugin4'
                }
            ]
        }
        expected_agents = {
            'agent1': 'agent1:plugins.plugin1',
            'agent2': 'agent2:plugins.plugin2'
        }
        expected_backends = {
            'backend1': 'backend1:plugins.plugin3',
            'backend2': 'backend2:plugins.plugin4'
        }

        loader = PluginLoader(config)
        loader.load_object = mock.Mock(spec=True, side_effect=load_object)
        agents, backends = loader.load_plugins()
        for key, value in agents.iteritems():
            self.assertTrue(key in expected_agents)
            self.assertEquals(value, expected_agents[key])
        for key, value in backends.iteritems():
            self.assertTrue(key in expected_backends)
            self.assertEquals(value, expected_backends[key])

    def test_load_object_external(self):
        """
        Tests the loading of classes by name

        """
        loader = PluginLoader({'agents': {}, 'backend': {}})
        params = {
            'plugin': 'fake_plugin.FakePlugin',
            'name': 'fake_name'
        }
        obj = loader.load_object(params)

    def test_load_object_internal(self):
        """
        Tests the loading of classes by name

        """
        loader = PluginLoader({'agents': {}, 'backend': {}})
        params = {
            'plugin': 'osprofiler.plugins.pluginbase.PluginBase',
            'name': 'PluginBase'
        }
        obj = loader.load_object(params)

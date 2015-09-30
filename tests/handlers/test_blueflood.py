import eventlet
import mock
import unittest

from bluefloodclient.client import Blueflood

import base

from osprofiler.handlers import blueflood


def side_effect_data(data):
    return data


class TestBluefloodHandler(unittest.TestCase):
    """
    Tests for the blueflood handler

    """
    mock_config = {
        'auth': {
            'auth_url': 'nonsense',
            'apikey': 'nonsense',
            'username': 'nonsense'
        }
    }

    @mock.patch('osprofiler.handlers.blueflood.Blueflood')
    def test_handle_data_simple(self, *mocked):
        handler = blueflood.BluefloodHandler(config=self.mock_config)
        handler.queue.put = mock.Mock(side_effect=side_effect_data)
        expected = {
            'sample.metric.1': 1,
            'sample.metric.2': 2,
            'sample.metric.3': 3,
            'sample.metric.4': 4
        }
        sample = {
            'metrics': [
                {
                    'sample.metric.1': 1,
                    'sample.metric.2': 2
                },
                {
                    'sample.metric.3': 3
                },
                {
                    'sample.metric.4': 4
                }
            ]
        }
        handler.handle(sample)
        for call in handler.queue.put.call_args_list:
            metric_dict = call[0][0]
            name = metric_dict['metricName']
            value = metric_dict['metricValue']
            self.assertTrue('ttlInSeconds' in metric_dict)
            self.assertTrue('collectionTime' in metric_dict)
            self.assertTrue('metricName' in metric_dict)
            self.assertTrue(name in expected)
            self.assertEquals(value, expected[name])

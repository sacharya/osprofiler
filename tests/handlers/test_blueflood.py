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
    def test_handle(self, *mocked):
        handler = blueflood.BluefloodHandler(config=self.mock_config)
        handler.queue.put = mock.Mock(side_effect=side_effect_data)
        expected = [
            {
                'name': 'sample.metric.1',
                'value': 1,
                'units': 'nonsenses'
            },
            {
                'name': 'sample.metric.2',
                'value': 2
            }
        ]
        sample = {
            'metrics': [
                {
                    'name': 'sample.metric.1',
                    'value': 1,
                    'units': 'nonsenses'
                },
                {
                    'name': 'sample.metric.2',
                    'value': 2
                },
            ]
        }
        handler.handle(sample)
        for call in handler.queue.put.call_args_list:
            metric_dict = call[0][0]
            name = metric_dict['metricName']
            value = metric_dict['metricValue']

            for e_metric in expected:
                if e_metric['name'] == name:
                    self.assertTrue('ttlInSeconds' in metric_dict)
                    self.assertTrue('collectionTime' in metric_dict)
                    self.assertTrue('metricName' in metric_dict)
                    self.assertEquals(value, e_metric['value'])
                    self.assertEquals(e_metric.get('units'),
                                      metric_dict.get('unit'))
                    break
            else:
                self.fail("Metric %s not found in expected" % name)

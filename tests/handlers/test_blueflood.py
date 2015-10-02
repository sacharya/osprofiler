import mock
import unittest

import base

from osprofiler.handlers import blueflood

mock_config = {
    'auth': {
        'auth_url': 'nonsense_url',
        'apikey': 'nonsense_key',
        'username': 'nonsense_user'
    },
    'batch_size': 123,
    'workers': 3
}


def side_effect_data(data):
    return data


class FakeWorker(object):
    pass


class TestBluefloodHandler(unittest.TestCase):
    """
    Tests for the blueflood handler

    """
    @mock.patch('osprofiler.handlers.blueflood.BluefloodWorker',
                return_value=FakeWorker())
    def test_init(self, mocked_worker):
        handler = blueflood.BluefloodHandler(config=mock_config)
        self.assertTrue(hasattr(handler, 'queue'))
        self.assertEquals(len(handler.workers), 3)

    @mock.patch('osprofiler.handlers.blueflood.BluefloodWorker',
                return_value=FakeWorker())
    def test_create_worker(self, mocked_worker):
        """
        Tests the create worker method

        """
        handler = blueflood.BluefloodHandler(config=mock_config)
        handler.workers = []
        self.assertEquals(len(handler.workers), 0)
        handler.create_worker()
        self.assertEquals(len(handler.workers), 1)
        args, kwargs = mocked_worker.call_args
        self.assertEquals(args[0], handler.queue)
        self.assertEquals(kwargs['config'], mock_config)

    @mock.patch('osprofiler.handlers.blueflood.Blueflood')
    def test_handle(self, *mocked):
        """
        Tests the handle method

        """
        handler = blueflood.BluefloodHandler(config=mock_config)
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


class TestBluefloodWorker(unittest.TestCase):
    """
    Tests the blueflood worker class

    """
    @mock.patch('osprofiler.handlers.blueflood.Blueflood')
    def test_init(self, mocked_client):
        """
        Tests worker init
        """
        mocked_queue = mock.Mock()
        worker = blueflood.BluefloodWorker(mocked_queue, mock_config)

        # Assert that configured batch size is the right batch size
        self.assertEquals(mock_config['batch_size'],
                          worker.batch_size)

        # Assert that the queue is the mocked queue
        self.assertEquals(mocked_queue, worker.queue)

        # Check call to blueflood client
        kwargs = mocked_client.call_args[1]
        self.assertEquals(kwargs['auth_url'],
                          mock_config['auth']['auth_url'])
        self.assertEquals(kwargs['apikey'],
                          mock_config['auth']['apikey'])
        self.assertEquals(kwargs['username'],
                          mock_config['auth']['username'])

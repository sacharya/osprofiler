import eventlet
import mock
import unittest

from bluefloodclient.client import Blueflood

import base

from osprofiler.handlers import elastic


class TestElasticHandler(unittest.TestCase):
    """
    Tests for the elastic search handler

    """

    @mock.patch('osprofiler.handlers.elastic.eventlet.queue.Queue')
    @mock.patch('osprofiler.handlers.elastic.elasticsearch.Elasticsearch')
    def test_client(self, mock_elastic, mock_queue):
        """
        Tests if the config is used to create a client

        """
        config = {
            'name': 'elastic',
            'host': 'myhost'
        }
        handler = elastic.ElasticSearchHandler(config=config)
        client_args = mock_elastic.call_args[0][0]
        self.assertTrue(isinstance(client_args, list))
        self.assertTrue(config['host'] in client_args)

    @mock.patch('osprofiler.handlers.elastic.eventlet.queue.Queue')
    @mock.patch('osprofiler.handlers.elastic.elasticsearch.Elasticsearch')
    def test_worker_config(self, mock_elastic, mock_queue):
        """
        Tests if the config is used to create a client

        """
        config = {
            'name': 'elastic',
            'batch_size': 123,
            'index_prefix': 'nonsense',
            'index_type': 'random'
        }
        handler = elastic.ElasticSearchHandler(config=config)
        self.assertEquals(handler.worker.batch_size, config['batch_size'])
        self.assertEquals(handler.worker.index_prefix, config['index_prefix'])
        self.assertEquals(handler.worker.index_type, config['index_type'])

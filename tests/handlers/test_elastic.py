import mock
import unittest

import base

from osprofiler.handlers import elastic

mock_config = {
    'name': 'elastic',
    'host': 'myhost',
    'batch_size': 123,
    'index_prefix': 'nonsense',
    'index_type': 'random',
    'workers': 3
}


class FakeWorker(object):
    pass


class TestElasticHandler(unittest.TestCase):
    """
    Tests for the elastic search handler

    """

    @mock.patch('osprofiler.handlers.elastic.ElasticSearchWorker',
                return_value=FakeWorker())
    def test_init(self, mocked_worker):
        """
        Tests init

        """
        handler = elastic.ElasticSearchHandler(config=mock_config)
        self.assertTrue(hasattr(handler, 'queue'))
        self.assertEquals(len(handler.workers), mock_config['workers'])

    @mock.patch('osprofiler.handlers.elastic.ElasticSearchWorker',
                return_value=FakeWorker())
    def test_create_worker(self, mocked_worker):
        """
        Tests worker creation

        """
        handler = elastic.ElasticSearchHandler(config=mock_config)
        handler.create_worker()
        self.assertEquals(len(handler.workers), mock_config['workers'] + 1)


class TestElasticsearchWorker(unittest.TestCase):
    """
    Tests the elastic search worker

    """
    @mock.patch('osprofiler.handlers.elastic.elasticsearch.Elasticsearch')
    def test_init(self, mocked_elastic):
        mock_queue = mock.Mock()
        worker = elastic.ElasticSearchWorker(mock_queue, config=mock_config)
        self.assertEquals(worker.batch_size, mock_config['batch_size'])
        self.assertEquals(worker.index_prefix, mock_config['index_prefix'])
        self.assertEquals(worker.index_type, mock_config['index_type'])
        client_args = mocked_elastic.call_args[0][0]
        self.assertTrue(isinstance(client_args, list))
        self.assertTrue(mock_config['host'] in client_args)

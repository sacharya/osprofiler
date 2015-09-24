import base
import unittest
import yaml

from osprofiler import utils


class TestConfig(unittest.TestCase):
    """
    Testing for configuration.

    """

    def test_non_exists(self):
        """
        Tests that a nonexisting file raises an exception

        """
        filename = "some_file_that_doesn't_exist"
        self.assertRaises(IOError, utils.read_config, filename)

    def test_good_config(self):
        """
        Tests that a valid yaml document can be read and that the
        result is a dictionary.

        """
        filename = "data/good_config"
        config = utils.read_config(filename)
        self.assertTrue(isinstance(config, dict))

    def test_bad_config(self):
        """
        Tests that a file with a invalid yaml raises an exception.

        """
        filename = "data/bad_config"
        self.assertRaises(yaml.YAMLError, utils.read_config, filename)

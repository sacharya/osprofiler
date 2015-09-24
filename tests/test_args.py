import base
import unittest

from osprofiler import args


class TestArgs(unittest.TestCase):
    """
    Tests the parser for arguments.

    """
    def test_defaults(self):
        """
        Tests default values for configuration

        """
        # Config ('-c', '--config')
        default = '/etc/osprofiler/osprofiler.conf'
        unparsed_args = []
        parsed_args = args.parser.parse_args(unparsed_args)
        self.assertTrue(hasattr(parsed_args, 'config'))
        self.assertEquals(parsed_args.config, default)

    def test_config_flags(self):
        """
        Tests config flags '-c' and '--config'

        """
        flag_dict = {
            '-c': '/etc/short',
            '--config': '/etc/long'
        }
        for flag, value in flag_dict.items():
            parsed_args = args.parser.parse_args([flag, value])
            self.assertEquals(parsed_args.config, value)

    def test_config_type(self):
        """
        Tests config option is string

        """
        values = ['string', '123']
        for v in values:
            parsed_args = args.parser.parse_args(['-c', v])
            self.assertTrue(isinstance(parsed_args.config, str))

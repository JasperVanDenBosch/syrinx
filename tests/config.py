from __future__ import annotations
from unittest import TestCase
from unittest.mock import patch, mock_open, Mock
from argparse import Namespace


class ConfigTests(TestCase):
    """test the configuration;
    should follow precedence; 
    CLI trumps config file,
    if no config file,
    have sensible defaults
    """

    @patch('syrinx.config.isfile')
    @patch('syrinx.config.open')
    def test_defaults(self, _, isfile):
        from syrinx.config import configure
        isfile.return_value = False
        ## if argument not supplied, the attribute is not set
        args = Namespace()
        config = configure(args)
        self.assertIsNone(config.domain)
        self.assertFalse(config.verbose)
        self.assertEqual(config.environment, 'default')

    @patch('syrinx.config.isfile')
    @patch('syrinx.config.open')
    def test_file(self, open, isfile):
        from syrinx.config import configure
        isfile.return_value = True
        fhandle = open.return_value.__enter__.return_value
        fhandle.read.return_value = """
            domain = "some.where.bla"
            verbose = true
            environment = "staging"
        """
        args = Namespace()
        args.domain = None
        args.verbose = None
        config = configure(args)
        self.assertEqual(config.domain, 'some.where.bla')
        self.assertTrue(config.verbose)
        self.assertEqual(config.environment, 'staging')

    @patch('syrinx.config.isfile')
    @patch('syrinx.config.open')
    def test_cli(self, open, isfile):
        from syrinx.config import configure
        isfile.return_value = True
        fhandle = open.return_value.__enter__.return_value
        fhandle.read.return_value = """
            domain = "some.where.bla"
            verbose = true
            environment = "staging"
        """
        args = Namespace()
        args.domain = 'not.there.bla'
        args.verbose = False
        args.environment = 'production'
        config = configure(args)
        self.assertEqual(config.domain, 'not.there.bla')
        self.assertFalse(config.verbose)
        self.assertEqual(config.environment, 'production')

    def test_configuration_stringifiable(self):
        """SyrinxConfiguration objects should convert to readable 
        string so we can log it in verbose mode.
        """
        from syrinx.config import SyrinxConfiguration
        config = SyrinxConfiguration()
        self.assertEqual(str(config), '')

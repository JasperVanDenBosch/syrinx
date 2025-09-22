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
    @patch('syrinx.config.open', new_callable=mock_open)
    def test_defaults(self, _, isfile):
        from syrinx.config import configure
        isfile.return_value = False
        ## if argument not supplied, the attribute is not set
        args = Namespace()
        config = configure(args)
        self.assertIsNone(config.domain)
        self.assertFalse(config.verbose)
        self.assertTrue(config.clean)
        self.assertEqual(config.environment, 'default')
        self.assertEqual(config.urlformat, 'filesystem')

    @patch('syrinx.config.isfile')
    @patch('syrinx.config.open', new_callable=mock_open)
    def test_file(self, mocked_open, isfile):
        from syrinx.config import configure
        isfile.return_value = True
        mocked_open().read.return_value = """
            domain = "some.where.bla"
            verbose = true
            environment = "staging"
            clean = false
            urlformat = "clean"
        """
        args = Namespace()
        config = configure(args)
        self.assertEqual(config.domain, 'some.where.bla')
        self.assertTrue(config.verbose)
        self.assertFalse(config.clean)
        self.assertEqual(config.environment, 'staging')
        self.assertEqual(config.urlformat, 'clean')

    @patch('syrinx.config.isfile')
    @patch('syrinx.config.open', new_callable=mock_open)
    def test_cli(self, mocked_open, isfile):
        from syrinx.config import configure
        isfile.return_value = True
        mocked_open().read.return_value = """
            clean = false
            domain = "some.where.bla"
            verbose = true
            environment = "staging"
            urlformat = "clean"
        """
        args = Namespace()
        args.domain = 'not.there.bla'
        args.verbose = False
        args.environment = 'production'
        args.clean = True
        args.urlformat = 'clean'
        config = configure(args)
        self.assertEqual(config.domain, 'not.there.bla')
        self.assertFalse(config.verbose)
        self.assertEqual(config.environment, 'production')
        self.assertTrue(config.clean)
        self.assertEqual(config.urlformat, 'clean')

    def test_configuration_stringifiable(self):
        """SyrinxConfiguration objects should convert to readable 
        string so we can log it in verbose mode.
        """
        from syrinx.config import SyrinxConfiguration
        config = SyrinxConfiguration()
        config.domain = 'some.where.bla'
        config.environment = 'default'
        config.verbose = False
        config.clean = True
        config.urlformat = 'filesystem'
        self.assertEqual(str(config), 
            '\tclean = true\n'
            '\tdomain = "some.where.bla"\n'
            '\tenvironment = "default"\n'
            '\tverbose = false\n'
            '\turlformat = "filesystem"'
        )

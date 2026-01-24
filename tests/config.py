from __future__ import annotations
from unittest import TestCase
from unittest.mock import patch, mock_open, Mock
from argparse import Namespace
from datetime import datetime, timezone


class ConfigTests(TestCase):
    """test the configuration;
    should follow precedence; 
    CLI trumps config file,
    if no config file,
    have sensible defaults
    """
    

    @patch('syrinx.config.read_branches')
    @patch('syrinx.config.isfile')
    @patch('syrinx.config.open', new_callable=mock_open)
    def test_defaults(self, _, isfile, mock_read_branches):
        from syrinx.config import configure
        from syrinx.branches import Branches
        isfile.return_value = False
        # Mock read_branches to return a Branches object
        mock_branches = Mock(spec=Branches)
        mock_branches.inner = {}
        mock_branches.update = Mock()
        mock_read_branches.return_value = mock_branches
        ## if argument not supplied, the attribute is not set
        args = Namespace()
        config = configure(args)
        self.assertTrue(config.clean)
        self.assertIsNone(config.domain)
        self.assertEqual(config.environment, 'default')
        self.assertFalse(config.leaf_pages)
        self.assertEqual(config.sitemap, 'opt-out')
        self.assertEqual(config.urlformat, 'filesystem')
        self.assertFalse(config.verbose)

    @patch('syrinx.config.read_branches')
    @patch('syrinx.config.isfile')
    @patch('syrinx.config.open', new_callable=mock_open)
    def test_file(self, mocked_open, isfile, mock_read_branches):
        from syrinx.config import configure
        from syrinx.branches import Branches
        isfile.return_value = True
        # Mock read_branches to return a Branches object
        mock_branches = Mock(spec=Branches)
        mock_branches.inner = {}
        mock_branches.update = Mock()
        mock_read_branches.return_value = mock_branches
        mocked_open().read.return_value = """
            clean = false
            domain = "some.where.bla"
            environment = "staging"
            leaf_pages = true
            urlformat = "clean"
            verbose = true
        """
        args = Namespace()
        config = configure(args)
        self.assertFalse(config.clean)
        self.assertEqual(config.domain, 'some.where.bla')
        self.assertEqual(config.environment, 'staging')
        self.assertTrue(config.leaf_pages)
        self.assertEqual(config.urlformat, 'clean')
        self.assertTrue(config.verbose)

    @patch('syrinx.config.read_branches')
    @patch('syrinx.config.isfile')
    @patch('syrinx.config.open', new_callable=mock_open)
    def test_cli(self, mocked_open, isfile, mock_read_branches):
        from syrinx.config import configure
        from syrinx.branches import Branches
        isfile.return_value = True
        # Mock read_branches to return a Branches object
        mock_branches = Mock(spec=Branches)
        mock_branches.inner = {}
        mock_branches.update = Mock()
        mock_read_branches.return_value = mock_branches
        mocked_open().read.return_value = """
            clean = false
            domain = "some.where.bla"
            environment = "staging"
            leaf_pages = true
            urlformat = "clean"
            verbose = true
        """
        args = Namespace()
        args.clean = True
        args.domain = 'not.there.bla'
        args.environment = 'production'
        args.leaf_pages = False
        args.urlformat = 'clean'
        args.verbose = False
        config = configure(args)
        self.assertTrue(config.clean)
        self.assertEqual(config.domain, 'not.there.bla')
        self.assertEqual(config.environment, 'production')
        self.assertFalse(config.leaf_pages)
        self.assertEqual(config.urlformat, 'clean')
        self.assertFalse(config.verbose)

    def test_configuration_stringifiable(self):
        """SyrinxConfiguration objects should convert to readable 
        string so we can log it in verbose mode.
        """
        from syrinx.config import SyrinxConfiguration
        config = SyrinxConfiguration()
        config.clean = True
        config.domain = 'some.where.bla'
        config.environment = 'default'
        config.leaf_pages = False
        config.sitemap = 'opt-out'
        config.urlformat = 'filesystem'
        config.verbose = False
        self.assertEqual(str(config), 
            '\tclean = true\n'
            '\tdomain = "some.where.bla"\n'
            '\tenvironment = "default"\n'
            '\tleaf_pages = false\n'
            '\tsitemap = "opt-out"\n'
            '\turlformat = "filesystem"\n'
            '\tverbose = false'
        )

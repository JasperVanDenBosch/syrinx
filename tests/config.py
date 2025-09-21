from __future__ import annotations
from unittest import TestCase
from unittest.mock import patch, mock_open, Mock
from datetime import datetime




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
        args = Mock()
        args.domain = None
        config = configure('/root/path/', args)
        self.assertIsNone(config.domain)

    @patch('syrinx.config.isfile')
    @patch('syrinx.config.open')
    def test_file(self, open, isfile):
        from syrinx.config import configure
        isfile.return_value = True
        fhandle = open.return_value.__enter__.return_value
        fhandle.readlines.return_value = ['domain = "some.where.bla"']
        args = Mock()
        args.domain = None
        config = configure('/root/path/', args)
        self.assertEqual(config.domain, 'some.where.bla')

    @patch('syrinx.config.isfile')
    @patch('syrinx.config.open')
    def test_cli(self, open, isfile):
        from syrinx.config import configure
        isfile.return_value = True
        fhandle = open.return_value.__enter__.return_value
        fhandle.readlines.return_value = ['domain = "some.where.bla"']
        args = Mock()
        args.domain = 'not.there.bla'
        config = configure('/root/path/', args)
        self.assertEqual(config.domain, 'not.there.bla')
from __future__ import annotations
from typing import TYPE_CHECKING
from unittest import TestCase
from unittest.mock import patch, Mock
from datetime import datetime


class ReadTests(TestCase):

    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    def test_read_BuildPage_branch_with_index(self, read_file, walk):
        """If index.md present on branch then set "BuildPage" to true
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md']),
            ('/pth/content/lorem', None, ['ipsum.md', 'index.md']),
        ]
        meta = Mock()
        from syrinx.read import read
        root = read('/pth', meta)
        self.assertTrue(root.branches[0].buildPage)

    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    def test_read_BuildPage_branch_without_index(self, read_file, walk):
        """If index.md absent on branch then set "BuildPage" to false
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md']),
            ('/pth/content/foo', None, ['bar.md']),
        ]
        meta = Mock()
        from syrinx.read import read
        root = read('/pth', meta)
        self.assertFalse(root.branches[0].buildPage)

    @patch('syrinx.read.walk')
    def test_read_Fail_if_index_missing(self, walk):
        """The root index.md is not optional,
        raise an exception if it's missing.
        """
        walk.return_value = [('/pth/content', None, ['other.md'])]
        meta = Mock()
        from syrinx.read import read
        from syrinx.exceptions import ContentError
        with self.assertRaisesRegex(ContentError, 'root index file missing'):
            read('/pth', meta)

    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    def test_read_adds_build_info(self, read_file, walk):
        """
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md']),
            ('/pth/content/foo', None, ['bar.md']),
        ]

        from syrinx.read import read
        meta = Mock()
        meta.environment = 'foo'
        meta.timestamp = dt = datetime.now()
        root = read('/pth', meta)
        self.assertEqual(root.meta.environment, 'foo')
        self.assertEqual(root.meta.timestamp, dt)
        self.assertEqual(root.branches[0].meta.environment, 'foo')
        self.assertEqual(root.branches[0].meta.timestamp, dt)
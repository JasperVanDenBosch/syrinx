from __future__ import annotations
from unittest import TestCase
from unittest.mock import patch, Mock


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
        config = Mock()
        from syrinx.read import read
        root = read('/pth', config)
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
        config = Mock()
        from syrinx.read import read
        root = read('/pth', config)
        self.assertFalse(root.branches[0].buildPage)

    @patch('syrinx.read.walk')
    def test_read_Fail_if_index_missing(self, walk):
        """The root index.md is not optional,
        raise an exception if it's missing.
        """
        walk.return_value = [('/pth/content', None, ['other.md'])]
        config = Mock()
        from syrinx.read import read
        from syrinx.exceptions import ContentError
        with self.assertRaisesRegex(ContentError, 'root index file missing'):
            read('/pth', config)

    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    @patch('syrinx.read.datetime')
    def test_read_adds_build_info(self, datetime, read_file, walk):
        """
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md']),
            ('/pth/content/foo', None, ['bar.md']),
        ]

        from syrinx.read import read
        config = Mock()
        config.environment = 'foo'
        root = read('/pth', config)
        self.assertEqual(root.meta.environment, 'foo')
        self.assertEqual(root.meta.timestamp, datetime.now())
        self.assertEqual(root.branches[0].meta.environment, 'foo')
        self.assertEqual(root.branches[0].meta.timestamp, datetime.now())

    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    def test_read_address(self, read_file, walk):
        """
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md']),
            ('/pth/content/foo', None, ['index.md', 'boz.md']),
            ('/pth/content/foo/bar', None, ['index.md']),
        ]
        from syrinx.read import read
        config = Mock()
        config.domain = 'loop.xyz'
        root = read('/pth', config)
        self.assertEqual(root.address, 'https://loop.xyz/')
        self.assertEqual(root.branches[0].address, 'https://loop.xyz/foo/')
        self.assertEqual(root.branches[0].branches[0].address,
            'https://loop.xyz/foo/bar/')

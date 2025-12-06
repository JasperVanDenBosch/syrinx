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
    @patch('syrinx.read.read_file')
    def test_read_BuildPage_leaf(self, read_file, walk):
        """Set "BuildPage" to false for leaves
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md']),
            ('/pth/content/lorem', None, ['ipsum.md', 'index.md']),
        ]
        config = Mock()
        from syrinx.read import read
        root = read('/pth', config)
        self.assertFalse(root.branches[0].leaves[0].buildPage)

    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    def test_read_BuildPage_leaf(self, read_file, walk):
        """Set "BuildPage" to true for leaves if `config.leaf_pages == True`
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md']),
            ('/pth/content/lorem', None, ['ipsum.md', 'index.md']),
        ]
        config = Mock()
        config.leaf_pages = True
        from syrinx.read import read
        root = read('/pth', config)
        self.assertTrue(root.branches[0].leaves[0].buildPage)

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
    @patch('syrinx.config.datetime')
    def test_read_adds_build_info(self, datetime, read_file, walk):
        """
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md']),
            ('/pth/content/foo', None, ['bar.md']),
        ]

        from syrinx.read import read
        from syrinx.config import BuildMetaInfo
        config = Mock()
        config.environment = 'foo'
        config.meta = BuildMetaInfo(config)
        root = read('/pth', config)
        self.assertEqual(root.meta.environment, 'foo')
        self.assertEqual(root.meta.timestamp, datetime.now())
        self.assertEqual(root.branches[0].meta.environment, 'foo')
        self.assertEqual(root.branches[0].meta.timestamp, datetime.now())

    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    def test_read_address_filesystem(self, read_file, walk):
        """With the "filesystem" style, terminal branches have trailing slashes,
        and leaves have file extensions.

        This style typically works out-of-the-box with web server software.
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md', 'tam.md']),
            ('/pth/content/foo', None, ['index.md', 'boz.md']),
            ('/pth/content/foo/bar', None, ['index.md']),
        ]
        from syrinx.read import read
        config = Mock()
        config.domain = 'loop.xyz'
        config.urlformat = 'filesystem'
        root = read('/pth', config)
        self.assertEqual(root.address, 'https://loop.xyz')
        self.assertEqual(root.branches[0].address, 'https://loop.xyz/foo/')
        self.assertEqual(root.branches[0].leaves[0].address,
                         'https://loop.xyz/foo/boz.html')
        self.assertEqual(root.branches[0].branches[0].address,
            'https://loop.xyz/foo/bar/')
        self.assertEqual(root.leaves[0].address, 'https://loop.xyz/tam.html')
        
    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    def test_read_address_clean(self, read_file, walk):
        """With the "clean" style, terminal branches and leaves
        do not have trailing slashes or file extensions
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md', 'tam.md']),
            ('/pth/content/bar', None, ['index.md', 'boz.md']),
            ('/pth/content/foo', None, ['index.md']),
            ('/pth/content/foo/bar', None, ['index.md']),
        ]
        from syrinx.read import read
        config = Mock()
        config.domain = 'loop.xyz'
        config.urlformat = 'clean'
        root = read('/pth', config)
        self.assertEqual(root.address, 'https://loop.xyz')
        # this page has sub-branches, i.e. is a directory, 
        # so comes with trailing slash:
        self.assertEqual(root.branches[0].address, 'https://loop.xyz/bar/')
        # this page has leaves, i.e. is a directory, 
        # so comes with trailing slash:
        self.assertEqual(root.branches[1].address, 'https://loop.xyz/foo/')
        # leaves dont get a trailing slash:
        self.assertEqual(root.branches[0].leaves[0].address,
                         'https://loop.xyz/bar/boz')
        # branches without sub-branches don't get a slash
        self.assertEqual(root.branches[1].branches[0].address,
                         'https://loop.xyz/foo/bar')
        # root leaf: no trailing slash
        self.assertEqual(root.leaves[0].address, 'https://loop.xyz/tam')

    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    def test_read_address_mkdocs(self, read_file, walk):
        """With the "mkdocs" style, all non-root urls have a 
        trailing slash.
        See https://github.com/mkdocs/mkdocs/issues/4040
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md', 'tam.md']),
            ('/pth/content/bar', None, ['index.md', 'boz.md']),
            ('/pth/content/foo', None, ['index.md']),
            ('/pth/content/foo/bar', None, ['index.md']),
        ]
        from syrinx.read import read
        config = Mock()
        config.domain = 'loop.xyz'
        config.urlformat = 'mkdocs'
        root = read('/pth', config)
        self.assertEqual(root.address, 'https://loop.xyz')
        # everything else comes with trailing slash:
        self.assertEqual(root.leaves[0].address, 'https://loop.xyz/tam/')
        self.assertEqual(root.branches[0].address, 'https://loop.xyz/bar/')
        self.assertEqual(root.branches[1].address, 'https://loop.xyz/foo/')
        self.assertEqual(root.branches[0].leaves[0].address,
                         'https://loop.xyz/bar/boz/')
        self.assertEqual(root.branches[1].branches[0].address,
                         'https://loop.xyz/foo/bar/')

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
        config.leaf_pages = False
        from syrinx.read import read
        root = read('/pth', config)
        self.assertFalse(root.branches[0].leaves[0].buildPage)

    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    def test_read_BuildPage_leaf_w_leaf_pages(self, read_file, walk):
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
        config.meta = BuildMetaInfo(config, '/pth')
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

    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    def test_read_name_root(self, read_file, walk):
        """Root node should have empty string as name
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md']),
        ]
        config = Mock()
        from syrinx.read import read
        root = read('/pth', config)
        self.assertEqual(root.name, '')

    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    def test_read_name_branch(self, read_file, walk):
        """Branch nodes should have name set to directory basename
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md']),
            ('/pth/content/lorem', None, ['index.md']),
        ]
        config = Mock()
        from syrinx.read import read
        root = read('/pth', config)
        self.assertEqual(root.branches[0].name, 'lorem')

    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    def test_read_name_leaf(self, read_file, walk):
        """Leaf nodes should have name set to filename without extension
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md']),
            ('/pth/content/foo', None, ['bar.md', 'index.md']),
        ]
        config = Mock()
        from syrinx.read import read
        root = read('/pth', config)
        self.assertEqual(root.branches[0].leaves[0].name, 'bar')

    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    def test_read_path_root(self, read_file, walk):
        """Root node path should be empty string
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md']),
        ]
        config = Mock()
        from syrinx.read import read
        root = read('/pth', config)
        self.assertEqual(root.path, '')

    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    def test_read_path_branch(self, read_file, walk):
        """Branch node path should be relative to content directory
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md']),
            ('/pth/content/lorem', None, ['index.md']),
            ('/pth/content/lorem/ipsum', None, ['index.md']),
        ]
        config = Mock()
        from syrinx.read import read
        root = read('/pth', config)
        self.assertEqual(root.branches[0].path, '/lorem')
        self.assertEqual(root.branches[0].branches[0].path, '/lorem/ipsum')

    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    def test_read_path_leaf(self, read_file, walk):
        """Leaf node path should be relative to content directory
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md']),
            ('/pth/content/foo', None, ['bar.md', 'index.md']),
        ]
        config = Mock()
        from syrinx.read import read
        root = read('/pth', config)
        self.assertEqual(root.branches[0].leaves[0].path, '/foo')

    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    def test_read_isLeaf_root(self, read_file, walk):
        """Root node should not be a leaf
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md']),
        ]
        config = Mock()
        from syrinx.read import read
        root = read('/pth', config)
        self.assertFalse(root.isLeaf)

    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    def test_read_isLeaf_branch(self, read_file, walk):
        """Branch nodes should not be leaves
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md']),
            ('/pth/content/lorem', None, ['index.md']),
        ]
        config = Mock()
        from syrinx.read import read
        root = read('/pth', config)
        self.assertFalse(root.branches[0].isLeaf)

    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    def test_read_isLeaf_leaf(self, read_file, walk):
        """Leaf nodes should have isLeaf set to True
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md']),
            ('/pth/content/foo', None, ['bar.md', 'index.md']),
        ]
        config = Mock()
        from syrinx.read import read
        root = read('/pth', config)
        self.assertTrue(root.branches[0].leaves[0].isLeaf)

    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    def test_read_sequenceNumber_default(self, read_file, walk):
        """When no SequenceNumber in frontmatter, should use default (SYS_MAX_SIZE)
        """
        read_file.return_value = dict(), ''
        walk.return_value = [
            ('/pth/content', None, ['index.md']),
            ('/pth/content/foo', None, ['bar.md', 'index.md']),
        ]
        config = Mock()
        from syrinx.read import read
        from sys import maxsize as SYS_MAX_SIZE
        root = read('/pth', config)
        self.assertEqual(root.sequenceNumber, SYS_MAX_SIZE)
        self.assertEqual(root.branches[0].sequenceNumber, SYS_MAX_SIZE)
        self.assertEqual(root.branches[0].leaves[0].sequenceNumber, SYS_MAX_SIZE)

    @patch('syrinx.read.walk')
    @patch('syrinx.read.read_file')
    def test_read_sequenceNumber_from_frontmatter(self, read_file, walk):
        """When SequenceNumber in frontmatter, should use that value
        """
        read_file.side_effect = [
            ({'SequenceNumber': 10}, ''),  # root index.md
            ({'SequenceNumber': 5}, ''),   # foo/index.md
            ({'SequenceNumber': 3}, ''),   # foo/bar.md
        ]
        walk.return_value = [
            ('/pth/content', None, ['index.md']),
            ('/pth/content/foo', None, ['bar.md', 'index.md']),
        ]
        config = Mock()
        from syrinx.read import read
        root = read('/pth', config)
        self.assertEqual(root.sequenceNumber, 10)
        self.assertEqual(root.branches[0].sequenceNumber, 5)
        self.assertEqual(root.branches[0].leaves[0].sequenceNumber, 3)

from unittest import TestCase
from unittest.mock import Mock
from parameterized import parameterized

class ContentNodeTests(TestCase):

    def test_follows_buildPage(self):
        from syrinx.node import ContentNode
        config = Mock()
        node = ContentNode(config)
        node.name = 'foo_bar'
        node.front = dict()
        self.assertEqual(node.title, 'Foo Bar')
        node.front['Title'] = 'Hello World'
        self.assertEqual(node.title, 'Hello World')

    @parameterized.expand([
        ['opt-out', False, True, 'a', False],
        ['opt-in', None, True, 'a', False],
        ['opt-in', False, True, 'a', False],
        ['opt-out', None, False, 'a', False],
        ['opt-out', True, False, 'a', False],
        ['opt-in', True, False, 'a', False],
        ['opt-out', None, True, None, False],
        ['opt-out', True, True, None, False],
        ['opt-in', True, True, None, False],
        ['opt-out', None, True, 'a', True],
        ['opt-out', True, True, 'a', True],
        ['opt-in', True, True, 'a', True],
    ])
    def test_includeInSitemap(self, cfg, fm, bld, url, exp):
        from syrinx.node import ContentNode
        config = Mock()
        config.sitemap = cfg
        config.domain = url
        config.leaf_pages = False
        node = ContentNode(config)
        node.source_path = 'a'
        node.name = 'b'
        node.front = dict()
        node.isLeaf = not bld
        node.path = ''
        if fm is not None:
            node.front['IncludeInSitemap'] = fm
        msg = (f'sitemap mode: {cfg}, frontmatter: {fm}, buildPage: {bld},'
            f' address: {url}, expected: {exp}')
        self.assertEqual(node.includeInSitemap, exp, msg)

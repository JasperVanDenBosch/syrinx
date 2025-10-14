from unittest import TestCase
from unittest.mock import Mock, patch

class BuildNodeTests(TestCase):

    @patch('syrinx.build.isfile')
    @patch('syrinx.build.open')
    def test_follows_buildPage(self, open, isfile):
        from syrinx.build import build_node
        node = Mock()
        root = Mock()
        env = Mock()
        isfile.return_value = True
        node.name = 'foo'
        node.branches = []
        node.leaves = []
        node.buildPage = False
        build_node(node, root, '', '', env)
        self.assertFalse(env.get_template().render.called)
        node.buildPage = True
        build_node(node, root, '', '', env)
        self.assertTrue(env.get_template().render.called)

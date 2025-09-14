from unittest import TestCase


class ContentNodeTests(TestCase):

    def test_follows_buildPage(self):
        from syrinx.read import ContentNode
        node = ContentNode()
        node.name = 'foo_bar'
        node.front = dict()
        self.assertEqual(node.title, 'Foo Bar')
        node.front['Title'] = 'Hello World'
        self.assertEqual(node.title, 'Hello World')

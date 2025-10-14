from unittest import TestCase
from unittest.mock import Mock
from parameterized import parameterized

class BuildTests(TestCase):

    @parameterized.expand([
        [False, 'page.jinja2'],
        [True, 'root.jinja2'],
    ])
    def test_choose_template_file_root(self, root_exists: bool, expected: str):
        from syrinx.build import choose_template_file
        node = Mock()
        node.isLeaf = False
        isfile = Mock()
        node.name = ''
        isfile.side_effect = lambda p: root_exists if p=='/t/root.jinja2' else True
        self.assertEqual(
            choose_template_file(node, isfile, '/t'),
            expected
        )

    @parameterized.expand([
        [False, 'page.jinja2'],
        [True, 'foo.jinja2'],
    ])
    def test_choose_template_file_other(self, foo_exists: bool, expected: str):
        from syrinx.build import choose_template_file
        node = Mock()
        node.isLeaf = False
        isfile = Mock()
        node.name = 'foo'
        isfile.side_effect = lambda p: foo_exists if p=='/t/foo.jinja2' else True
        self.assertEqual(
            choose_template_file(node, isfile, '/t'),
            expected
        )

    @parameterized.expand([
        [False, False, 'page.jinja2'],
        [False, True, 'leaf.jinja2'],
        [True, True, 'foo.jinja2'],
    ])
    def test_choose_template_file_leaf(self, foo_exists: bool, leaf_exists: bool, expected: str):
        """Prioritize a named template, then a "leaf" template, and fallback
        to a general "page" template.

        Args:
            foo_exists (bool): A template matching the node's name exists
            leaf_exists (bool): A leaf.jinja2 template exists
            expected (str): The expected chosen template
        """
        from syrinx.build import choose_template_file
        node = Mock()
        node.isLeaf = True
        isfile = Mock()
        node.name = 'foo'
        exist_files = {
            '/t/foo.jinja2': foo_exists,
            '/t/leaf.jinja2': leaf_exists,
            '/t/page.jinja2': True,
        }
        isfile.side_effect = lambda p: exist_files[p]
        self.assertEqual(
            choose_template_file(node, isfile, '/t'),
            expected
        )

    def test_choose_template_file_none(self):
        """If no template is available, throw exception
        """
        from syrinx.build import choose_template_file
        from syrinx.exceptions import ThemeError
        node = Mock()
        isfile = Mock()
        node.name = 'foo'
        isfile.side_effect = lambda p: False
        with self.assertRaisesRegex(ThemeError, 'Missing template for "foo"'):
            choose_template_file(node, isfile, '/t')

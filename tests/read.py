from unittest import TestCase
from unittest.mock import patch


class ReadTests(TestCase):

    @patch('syrinx.read.walk')
    def test_read_BuildPage(self, walk):
        """
        FrontMatter "BuildPage" attribute:
        - if index.md present and has "BuildPage", use this
        - if index.md present then set "BuildPage" to true
        - if index.md absent then set "BuildPage" to false
        """
        walk.return_value = [('/pth/content', None, 'other.md')]
        from syrinx.read import read
        self.fail()

    @patch('syrinx.read.walk')
    def test_read_Fail_if_index_missing(self, walk):
        """The root index.md is not optional,
        raise an exception if it's missing.
        """
        walk.return_value = [('/pth/content', None, 'other.md')]
        from syrinx.read import read
        from syrinx.exceptions import ContentError
        with self.assertRaisesRegex(ContentError, 'root index file missing'):
            read('/pth')

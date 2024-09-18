from unittest import TestCase
from unittest.mock import Mock


class ReadTests(TestCase):

    def test_read_BuildPage(self):
        """
        FrontMatter "BuildPage" attribute:
        - if index.md present and has "BuildPage", use this
        - if index.md present then set "BuildPage" to true
        - if index.md absent then set "BuildPage" to false
        """
        self.fail()

    def test_read_Fail_if_index_missing(self):
        """The root index.md is not optional,
        raise an exception if it's missing.
        """
        self.fail()

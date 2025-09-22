from __future__ import annotations
from typing import Optional
from unittest import TestCase
from unittest.mock import Mock
from datetime import datetime


class SitemapTests(TestCase):

    def test_collect_urls(self):
        """Function should find all nodes that should be included in sitemap
        and add their canonical url and last modified datetime to the list.

        Should skip nodes that are not build, or lack a valid url or last modified.
        """
        from syrinx.sitemap import collect_urls
        root = self.makeNode(True, None, None)
        root.branches = []
        root.leaves = []
        urls = collect_urls(root)
        self.assertEqual(len(urls), 21)
        self.assertEqual(urls[0], ('', ))

    def makeNode(self, build: bool, url: Optional[str], dt: Optional[datetime]):
        node = Mock()
        node.buildPage = build
        node.lastModified = dt
        node.address = url
        node.branches = []
        node.leaves = []
        return node

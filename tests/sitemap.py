from __future__ import annotations
from typing import Optional
from unittest import TestCase
from unittest.mock import Mock
from datetime import datetime, UTC


class SitemapTests(TestCase):

    def test_collect_urls(self):
        """Function should find all nodes that should be included in sitemap
        and add their canonical url and last modified datetime to the list.

        Should skip nodes that are not build, or lack a valid url or last modified.
        """
        from syrinx.sitemap import collect_urls
        dt1 = datetime(2025, 9, 23, 10)
        dt2 = datetime(2025, 9, 23, 12)
        dt3 = datetime(2025, 9, 23, 14)
        aaa = self.makeNode(False, None, dt3)
        aab = self.makeNode(True, 'foo.bar/a/a/b/', dt2)
        aac = self.makeNode(False, None, dt1)
        aad = self.makeNode(True, 'foo.bar/a/a/c.html', None)
        aa = self.makeNode(True, 'foo.bar/a/a/', dt2)
        aa.branches = [aaa, aab]
        aa.leaves = [aac, aad]
        ab = self.makeNode(False, 'foo.bar/a/b', dt3)
        a = self.makeNode(True, 'foo.bar/a/', dt1)
        a.branches = [aa, ab]
        b = self.makeNode(True, 'foo.bar/b', dt2)
        root = self.makeNode(True, 'foo.bar', dt1)
        root.branches = [a]
        root.leaves = [b]
        urls = collect_urls(root)
        self.assertEqual(len(urls), 6)
        self.assertEqual(
            urls,
            [
                ('foo.bar', dt1),
                ('foo.bar/b', dt2),
                ('foo.bar/a/', dt1),
                ('foo.bar/a/a/', dt2),
                ('foo.bar/a/a/c.html', None),
                ('foo.bar/a/a/b/', dt2),
            ]
        )

    def test_generate(self):
        """Should generate the string content of an xml sitemap
        from the list of url, datetime tuples passed.
        """
        self.maxDiff = 900
        from syrinx.sitemap import generate_sitemap
        output = generate_sitemap(
            [
                ('https://meadows-research.com/signin', datetime(2025, 9, 22, tzinfo=UTC)),
                ('https://syrinx.site/docs#bla', None)
            ]
        )
        
        self.assertEqual(
            output,
            """
            <?xml version="1.0" encoding="UTF-8"?>
            <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
                <url><loc>https://meadows-research.com/signin</loc><lastmod>2025-09-22</lastmod></url>
                <url><loc>https://syrinx.site/docs#bla</loc></url>
            </urlset>
            """.replace('            ', '').strip()
        )

    def makeNode(self, include: bool, url: Optional[str], dt: Optional[datetime]):
        node = Mock()
        node.includeInSitemap = include
        node.lastModified = dt
        node.address = url
        node.branches = []
        node.leaves = []
        return node

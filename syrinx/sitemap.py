from __future__ import annotations
from typing import TYPE_CHECKING, List, Tuple, Optional
if TYPE_CHECKING:
    from syrinx.node import ContentNode
    from datetime import datetime
    ListOfUrls = List[Tuple[str, Optional[datetime]]]


def collect_urls(node: ContentNode) -> ListOfUrls:
    urls = []
    if node.includeInSitemap and node.address:
        urls.append((node.address, node.lastModified))

    for leaf in node.leaves:
        urls += collect_urls(leaf)

    for branch in node.branches:
        urls += collect_urls(branch)

    return urls


def generate_sitemap(urls: ListOfUrls) -> str:
    """Sitemap content string from list of url, datetime tuples
    """
    s = '<?xml version="1.0" encoding="UTF-8"?>\n'
    s += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for (url, dt) in urls:
        lm = f'<lastmod>{dt.date().isoformat()}</lastmod>' if dt else ''
        s += f'    <url><loc>{url}</loc>{lm}</url>\n'
    s += '</urlset>'
    return s

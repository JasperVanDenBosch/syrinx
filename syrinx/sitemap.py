from __future__ import annotations
from typing import TYPE_CHECKING, List, Tuple
if TYPE_CHECKING:
    from syrinx.node import ContentNode
    from datetime import datetime
    ListOfUrls = List[Tuple[str, datetime]]


def collect_urls(node: ContentNode) -> ListOfUrls:
    urls = []
    if node.buildPage and node.address and node.lastModified:
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
        s += f'    <url><loc>{url}</loc><lastmod>{dt.isoformat()}</lastmod></url>\n'
    s += '</urlset>'
    return s

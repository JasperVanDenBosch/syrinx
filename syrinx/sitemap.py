from __future__ import annotations
from typing import TYPE_CHECKING, List, Tuple
if TYPE_CHECKING:
    from syrinx.node import ContentNode
    from datetime import datetime
    ListOfUrls = List[Tuple[str, datetime]]


"""
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{% for url in urls %}
    <url>
        <loc>{{ url[0] }}</loc>
        <lastmod>{{ url[1] }}</lastmod>
    </url>
{% endfor %}
</urlset>
"""


def collect_urls(node: ContentNode) -> ListOfUrls:
    urls = []
    if node.buildPage and node.address and node.lastModified:
        urls.append((node.address, node.lastModified))

    for leaf in node.leaves:
        urls += collect_urls(leaf)

    for branch in node.branches:
        urls += collect_urls(branch)

    return urls


def generate_sitemap(root: ContentNode, add: ListOfUrls) -> str:
    urls = collect_urls(root) + add
    ## FORGET JINJA, DO WITH REGULAR STR
    return ''

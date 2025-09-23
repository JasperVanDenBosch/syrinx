"""Helper tool to check if the entries in a generated sitemap
correspond to live pages with matching canonical links.
"""
import sys
from os.path import abspath, join
import xml.etree.ElementTree as ET
from urllib.request import urlopen

dir_path = abspath(sys.argv[1])
sitemap_root = ET.parse(join(dir_path, 'sitemap.xml')).getroot()
for child in sitemap_root:
    loc = child[0]
    assert loc is not None
    assert loc.text is not None
    with urlopen(loc.text) as response:
        body = response.read()
    print(body)
    page_root = ET.fromstring(body)
    canonical_link = page_root.find(".//link[@rel='canonical']")
    print(canonical_link)
    print(f'OK {loc.text}')

"""Helper tool to check if the entries in a generated sitemap
correspond to live pages with matching canonical links.
"""
import sys
from os.path import abspath, join
import xml.etree.ElementTree as ET
from lxml.etree import XMLParser
from urllib.request import urlopen
from time import sleep

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

dir_path = abspath(sys.argv[1])
sitemap_root = ET.parse(join(dir_path, 'sitemap.xml')).getroot()
parser = XMLParser(recover=True)
for child in sitemap_root:
    loc = child[0]
    assert loc is not None
    assert loc.text is not None
    with urlopen(loc.text) as response:
        body = response.read()
    sleep(0.3)
    stat_col = bcolors.OKGREEN if response.status == 200 else bcolors.FAIL
    print(f'{stat_col}{response.status}{bcolors.ENDC} {loc.text}')
    page_root = ET.fromstring(body, parser=parser)
    canonical_link = page_root.find(".//link[@rel='canonical']")
    if canonical_link is None:
        print(f'{bcolors.WARNING}\t missing canonical{bcolors.ENDC}')
    else:
        canonical_href = canonical_link.attrib['href']
        if canonical_href != loc.text:
            print('{bcolors.WARNING}\t canonical mismatch{bcolors.ENDC}')

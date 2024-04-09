from __future__ import annotations
from typing import List, Dict, TYPE_CHECKING
import copy
#import xml.etree.ElementTree as ET
import lxml.etree as ET


def processor(html: str, xpath: str, tag:str, attribs: Dict[str, str]) -> str:
    root = ET.fromstring(html)
    matches = root.findall(xpath)
    for m, match in enumerate(matches):
        new = ET.Element(tag)
        new.append(copy.deepcopy(match))
        matches[m].getparent().replace(match, new)
    return ET.tostring(root, encoding='utf8')
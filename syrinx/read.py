from __future__ import annotations
from typing import List, Dict, Tuple
from os.path import dirname, basename, join
from os import walk
import tomllib
from markdown import markdown
from sys import maxsize as SYS_MAX_SIZE
from syrinx.exceptions import ContentError

"""
This section is just about reading and interpreting the content
"""

class ContentNode:
    name: str
    leaves: List[ContentNode]
    branches: List[ContentNode]
    content_html: str
    front: Dict[str, str]
    sequenceNumber: int
    buildPage: bool

    def __init__(self):
        self.buildPage = False
        self.leaves = []
        self.branches = []
        self.sequenceNumber = SYS_MAX_SIZE

    @property
    def title(self) -> str:
        return self.name.replace('_', ' ').title()

def reorder_children(node: ContentNode):
    node.leaves = sorted(node.leaves, key=lambda n: (n.sequenceNumber, n.name))
    node.branches = sorted(node.branches, key=lambda n: (n.sequenceNumber, n.name))
    for child in node.branches:
        reorder_children(child)


def read_file(fpath: str) -> Tuple[Dict, str]:
    with open(fpath) as fhandle:
        lines = fhandle.readlines()
    markers = [l for (l, line) in enumerate(lines) if line.strip() == '+++']
    assert len(markers) == 2
    fm_string = ''.join(lines[1:markers[1]])
    fm_dict = tomllib.loads(fm_string)
    md_content = ''.join(lines[markers[1]+1:])
    return fm_dict, md_content


def read(root_dir: str) -> ContentNode:

    content_dir = join(root_dir, 'content')

    tree: Dict[str, ContentNode] = dict()
    root = ContentNode()
    root.name = ''
    for (dirpath, _, fnames) in walk(content_dir):

        indexNode = ContentNode()
        indexNode.name = basename(dirpath)
        if dirpath == content_dir:
            indexNode = root
            if 'index.md' not in fnames:
                raise ContentError('root index file missing') 
        else:
            parent = tree[dirname(dirpath)]
            parent.branches.append(indexNode)
        tree[dirpath] = indexNode

        ## ideally process the index page first (not sure if this is necessary?)
        if 'index.md' in fnames:
            fnames.insert(0, fnames.pop(fnames.index('index.md')))
        for fname in fnames:
            fparts = fname.split('.')
            ext = fparts[-1]
            if ext != 'md':
                continue
            name = fparts[0]

            fm_dict, md_content = read_file(join(dirpath, fname))

            if name == 'index':
                node = indexNode
            else:
                node = ContentNode()
                node.name = name
                indexNode.leaves.append(node)
            
            node.front = fm_dict
            node.content_html = markdown(md_content)
            if 'SequenceNumber' in fm_dict:
                node.sequenceNumber = fm_dict['SequenceNumber']
            node.buildPage = True

    reorder_children(root)

    return root

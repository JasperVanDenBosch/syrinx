from __future__ import annotations
from typing import List, Dict
from os.path import dirname, basename, join
import os
import tomllib
from markdown import markdown

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

def reorder_children(node: ContentNode):
    node.leaves = sorted(node.leaves, key=lambda n: (n.sequenceNumber, n.name))
    node.branches = sorted(node.branches, key=lambda n: (n.sequenceNumber, n.name))
    for child in node.branches:
        reorder_children(child)


def read(root_dir: str) -> ContentNode:

    
    content_dir = join(root_dir, 'content')


    tree: Dict[str, ContentNode] = dict()
    root = ContentNode()
    root.name = ''
    for (dirpath, dirnames, fnames) in os.walk(content_dir):

        ## ideally process the index page first (not sure if this is necessary?)
        index_index = fnames.index('index.md')
        fnames.insert(0, fnames.pop(index_index))

        indexNode = ContentNode()
        indexNode.name = basename(dirpath)
        if dirpath == content_dir:
            indexNode = root
        else:
            parent = tree[dirname(dirpath)]
            parent.branches.append(indexNode)
        tree[dirpath] = indexNode
        for fname in fnames:
            fparts = fname.split('.')
            ext = fparts[-1]
            if ext != 'md':
                continue
            name = fparts[0]

            in_fpath = join(dirpath, fname)

            with open(in_fpath) as fhandle:
                lines = fhandle.readlines()

            markers = [l for (l, line) in enumerate(lines) if line.strip() == '+++']
            assert len(markers) == 2
            fm_string = ''.join(lines[1:markers[1]])
            fm_dict = tomllib.loads(fm_string)
            md_content = ''.join(lines[markers[1]+1:])

            if name == 'index':
                node = indexNode
            else:
                node = ContentNode()
                node.name = name
                indexNode.leaves.append(node)
            
            node.leaves = []
            node.branches = []
            node.front = fm_dict
            node.content_html = markdown(md_content)
            node.sequenceNumber = int(fm_dict.get('SequenceNumber', '99999'))

    reorder_children(root)

    return root

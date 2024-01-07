from __future__ import annotations
from typing import List, Dict
from os.path import abspath, dirname, isdir, basename, join
import os
from markdown import markdown
import sys

"""
This section is just about reading and interpreting the content
"""

class ContentNode:
    name: str
    children: List[ContentNode]
    content_html: str
    front: Dict[str, str]

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
            parent.children.append(indexNode)
        tree[dirpath] = indexNode
        for fname in fnames:
            name = fname.split('.')[0]

            in_fpath = join(dirpath, fname)

            with open(in_fpath) as fhandle:
                lines = fhandle.readlines()

            markers = [l for (l, line) in enumerate(lines) if line.strip() == '---']
            assert len(markers) == 2
            fm_lines = [line.strip() for line in lines[1:markers[1]]]
            fm_dict = dict()
            for line in fm_lines:
                parts = line.split(':')
                key = parts[0]
                val = line[(len(key)+1):].strip()
                fm_dict[key] = val

            md_content = ''.join(lines[markers[1]:])

            if name == 'index':
                node = indexNode
            else:
                node = ContentNode()
                node.name = name
                indexNode.children.append(node)
            
            node.children = []
            node.front = fm_dict
            node.content_html = markdown(md_content)

    return root

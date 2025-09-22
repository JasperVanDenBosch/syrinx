from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Tuple
from os.path import dirname, basename, join
from os import walk
import tomllib
import logging
from markdown import markdown
from syrinx.exceptions import ContentError
from syrinx.node import ContentNode, BuildMetaInfo
if TYPE_CHECKING:
    from syrinx.config import SyrinxConfiguration
logger = logging.getLogger(__name__)
"""
This section is just about reading and interpreting the content
"""


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


def read(root_dir: str, config: SyrinxConfiguration) -> ContentNode:

    meta = BuildMetaInfo(config)
    content_dir = join(root_dir, 'content')

    tree: Dict[str, ContentNode] = dict()
    root = ContentNode(meta, config)
    root.name = ''
    root.meta = meta
    for (dirpath, _, fnames) in walk(content_dir):

        indexNode = ContentNode(meta, config)
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
                node = ContentNode(meta, config)
                node.name = name
                node.isLeaf = True
                indexNode.leaves.append(node)
            node.path = dirpath.replace(content_dir, '')
            
            node.front = fm_dict
            node.content_html = markdown(md_content)
            if 'SequenceNumber' in fm_dict:
                node.sequenceNumber = fm_dict['SequenceNumber']
            node.buildPage = True
            rel_path = join(dirpath.replace(content_dir, ""), fname)
            logger.info(f'Read {rel_path}')

    reorder_children(root)

    return root

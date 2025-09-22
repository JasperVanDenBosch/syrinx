from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Tuple, Optional
from os.path import dirname, basename, join
from os import walk
import tomllib
import logging
from markdown import markdown
from sys import maxsize as SYS_MAX_SIZE
from syrinx.exceptions import ContentError
from datetime import datetime, UTC
from importlib.metadata import version
if TYPE_CHECKING:
    from syrinx.config import SyrinxConfiguration
logger = logging.getLogger(__name__)
"""
This section is just about reading and interpreting the content
"""


class BuildMetaInfo:

    def __init__(self, config: SyrinxConfiguration) -> None:
        self.environment = config.environment
        self.timestamp = datetime.now(tz=UTC)
        self.syrinx_version = version('syrinx')


class ContentNode:
    name: str
    leaves: List[ContentNode]
    branches: List[ContentNode]
    content_html: str
    front: Dict[str, str]
    sequenceNumber: int
    buildPage: bool
    path: str
    meta: BuildMetaInfo
    config: SyrinxConfiguration

    def __init__(self, meta: BuildMetaInfo, config: SyrinxConfiguration):
        self.buildPage = False
        self.leaves = []
        self.branches = []
        self.sequenceNumber = SYS_MAX_SIZE
        self.meta = meta
        self.config = config

    @property
    def title(self) -> str:
        if 'Title' in self.front:
            return self.front['Title']
        else:
            return self.name.replace('_', ' ').title()
        
    @property
    def address(self) -> Optional[str]:
        """Full, canonical URL of this node
        """
        if self.config.domain is not None:
            if self.config.urlformat == 'clean':
                return f'https://{self.config.domain}{self.path}'
            else:
                return f'https://{self.config.domain}{self.path}/'

    @property
    def lastModified(self) -> Optional[str]:
        return self.front.get('LastModified')


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
                node.path = dirpath.replace(content_dir, '')
            else:
                node = ContentNode(meta, config)
                node.name = name
                node.path = join(dirpath.replace(content_dir, ''), node.name)
                indexNode.leaves.append(node)
            
            node.front = fm_dict
            node.content_html = markdown(md_content)
            if 'SequenceNumber' in fm_dict:
                node.sequenceNumber = fm_dict['SequenceNumber']
            node.buildPage = True
            rel_path = join(dirpath.replace(content_dir, ""), fname)
            logger.info(f'Read {rel_path}')

    reorder_children(root)

    return root

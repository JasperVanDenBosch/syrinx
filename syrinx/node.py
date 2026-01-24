from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Optional
from sys import maxsize as SYS_MAX_SIZE
from os.path import dirname, basename
from datetime import datetime
if TYPE_CHECKING:
    from syrinx.config import SyrinxConfiguration, BuildMetaInfo


def makeBranchNode(config: SyrinxConfiguration, name: str) -> ContentNode:
    node = ContentNode(config)
    node.name = name
    node.isLeaf = False
    return node


def makeLeafNode(config: SyrinxConfiguration) -> ContentNode:
    node = ContentNode(config)
    node.isLeaf = True
    return node


class ContentNode:
    name: str
    leaves: List[ContentNode]
    branches: List[ContentNode]
    content_html: str
    front: Dict[str, str]
    path: str
    source_path: str
    config: SyrinxConfiguration
    isLeaf: bool
    fpath: str

    def __init__(self, config: SyrinxConfiguration):
        self.leaves = []
        self.branches = []
        self.front = {}
        self.config = config
        self.isLeaf = False
        self.source_path = ''

    def setContent(self, fpath: str, front: Dict[str, str], html: str) -> None:
        self.fpath = fpath
        self.front = front
        self.content_html = html
        self.source_path = fpath
        self.path = dirname(fpath)
        if self.path == '/':
            self.path = ''
        if self.isLeaf:
            fparts = basename(fpath).split('.')
            self.name = fparts[0]

    @property
    def meta(self) -> BuildMetaInfo:
        return self.config.meta

    @property
    def sequenceNumber(self) -> int:
        if 'SequenceNumber' in self.front:
            return self.front['SequenceNumber']
        else:
            return SYS_MAX_SIZE
        
    @property
    def buildPage(self) -> bool:
        if self.isLeaf and not self.config.leaf_pages:
            return False
        elif not self.source_path:
            return False
        else:
            return True

    @property
    def title(self) -> str:
        if 'Title' in self.front:
            return self.front['Title']
        else:
            return self.name.replace('_', ' ').title()
        
    @property
    def address(self) -> Optional[str]:
        """Full, canonical URL of this node

        Returns None if no domain configured. Applies one of three styles
        based on the *urlformat* config directive.
        """
        if self.config.domain is None:
            ## can't make an address if we don't know the domain
            return
        is_directory = any(self.branches) or any(self.leaves)
        trail = ''
        if len(self.name):
            if self.isLeaf:
                trail = f'/{self.name}'
                if self.config.urlformat == 'filesystem':
                    trail += '.html'
                elif self.config.urlformat == 'mkdocs':
                    trail += '/'
            elif is_directory or self.config.urlformat != 'clean':
                trail = '/'
        return f'https://{self.config.domain}{self.path}{trail}'

    @property
    def lastModified(self) -> Optional[datetime]:
        # First check for direct LastModified entry
        if 'LastModified' in self.front:
            # Convert string datetime to datetime object
            return datetime.fromisoformat(self.front['LastModified'])
        
        # If not present, check for LastModifiedBranch entry
        if 'LastModifiedBranch' in self.front:
            branch_name = self.front['LastModifiedBranch']
            # warn if modified, but on new branch
            self.config.branches.warnIfModifiedNodeHasOutdatedBranch(self, branch_name)
            # Return datetime object directly from branches
            return self.config.branches.get_lastmodified(branch_name)

        return None
    
    @property
    def includeInSitemap(self) -> bool:
        if not self.buildPage:
            return False
        if self.address is None:
            return False
        default = {'opt-in': False, 'opt-out': True}[self.config.sitemap]
        iis = self.front.get('IncludeInSitemap', default)
        if not isinstance(iis, bool):
            raise ValueError('IncludeInSitemap config entry must be boolean')
        return iis

from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Optional
from sys import maxsize as SYS_MAX_SIZE
from datetime import datetime, UTC
from importlib.metadata import version
if TYPE_CHECKING:
    from syrinx.config import SyrinxConfiguration


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
    isLeaf: bool

    def __init__(self, meta: BuildMetaInfo, config: SyrinxConfiguration):
        self.buildPage = False
        self.leaves = []
        self.branches = []
        self.sequenceNumber = SYS_MAX_SIZE
        self.meta = meta
        self.config = config
        self.isLeaf = False

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
    def lastModified(self) -> Optional[str]:
        return self.front.get('LastModified')
    
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

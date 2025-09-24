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

        Returns None if no domain configured. Applies one of two styles
        based on the *urlformat* config directive.
        """
        is_directory = any(self.branches) or any(self.leaves)
        if self.config.domain is not None:
            trail = ''
            if len(self.path):
                if self.isLeaf:
                    trail = f'/{self.name}'
                    if self.config.urlformat == 'filesystem':
                        trail += '.html'
                elif is_directory or self.config.urlformat == 'filesystem':
                    trail = '/'
                    
            return f'https://{self.config.domain}{self.path}{trail}'

    @property
    def lastModified(self) -> Optional[str]:
        return self.front.get('LastModified')

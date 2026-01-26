from __future__ import annotations
import logging
from typing import Optional, TYPE_CHECKING
from os.path import isfile, join, abspath
from datetime import datetime, UTC
from importlib.metadata import version
from syrinx.branches import read_branches
if TYPE_CHECKING:
    from argparse import Namespace
    from syrinx.branches import Branches


class BuildMetaInfo:

    def __init__(self, config: SyrinxConfiguration, root_dir: str) -> None:
        self.environment = config.environment
        self.timestamp = datetime.now(tz=UTC)
        self.syrinx_version = version('syrinx')
        self.root_dir = root_dir



class SyrinxConfiguration:
    clean: bool
    domain: Optional[str]
    environment: str
    leaf_pages: bool
    sitemap: str
    urlformat: str
    verbose: bool
    branches: Branches
    meta: BuildMetaInfo

    def __str__(self) -> str:
        lines = []
        KEYS = ('clean', 'domain', 'environment', 'leaf_pages', 
                'sitemap', 'urlformat', 'verbose')
        for key in KEYS:
            val = getattr(self, key)
            if isinstance(val, str):
                val = f'"{val}"'
            if isinstance(val, bool):
                val = str(val).lower()
            lines.append(f'\t{key} = {val}')
        return '\n'.join(lines)


def configure(args: Namespace) -> SyrinxConfiguration:
    config = SyrinxConfiguration()
    config.clean = True
    config.domain = None
    config.environment = 'default'
    config.leaf_pages = False
    config.sitemap = 'opt-out'
    config.urlformat = 'filesystem'
    config.verbose = False



    root_dir = getattr(args, 'dir', '.')
    cfg_fpath = join(abspath(root_dir), 'syrinx.cfg')
    if isfile(cfg_fpath):
        with open(cfg_fpath) as fhandle:
            content = fhandle.read()
            #print(content)
            for line in content.splitlines():
                if '=' not in line:
                    continue
                key, val, *_ = [p.strip() for p in line.split('=')]
                val = val.strip('"')
                if key == 'clean':
                    config.clean = val.lower() == 'true'
                elif key == 'domain':
                    config.domain = val
                elif key == 'environment':
                    config.environment = val
                elif key == 'leaf_pages':
                    config.leaf_pages = val.lower() == 'true'
                elif key == 'sitemap':
                    if val not in ('opt-in', 'opt-out'):
                        raise ValueError('Configuration option "sitemap" must'
                                         ' be one of "opt-in", "opt-out".')
                    config.sitemap = val
                elif key == 'urlformat':
                    config.urlformat = val
                elif key == 'verbose':
                    config.verbose = val.lower() == 'true'
                else:
                    raise ValueError(f'Unknown configuration entry: {key}')

    for key in ('clean', 'domain', 'verbose', 'environment', 'leaf_pages', 'urlformat'):
        if hasattr(args, key):
            setattr(config, key, getattr(args, key))

    if config.verbose:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.info('Configuration:\n'+str(config))

    config.meta = BuildMetaInfo(config, root_dir)
    config.branches = read_branches(root_dir)
    config.branches.update(config.meta, root_dir)
    return config

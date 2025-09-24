from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from os.path import isfile, join, abspath
if TYPE_CHECKING:
    from argparse import Namespace



class SyrinxConfiguration:
    clean: bool
    domain: Optional[str]
    environment: str
    verbose: bool
    urlformat: str

    def __str__(self) -> str:
        lines = []
        for key in ('clean', 'domain', 'environment', 'verbose', 'urlformat'):
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
    config.verbose = False
    config.environment = 'default'
    config.urlformat = 'filesystem'
    root_dir = getattr(args, 'root_dir', '.')
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
                if key == 'domain':
                    config.domain = val
                if key == 'verbose':
                    config.verbose = val.lower() == 'true'
                if key == 'environment':
                    config.environment = val
                if key == 'urlformat':
                    config.urlformat = val

    for key in ('clean', 'domain', 'verbose', 'environment', 'urlformat'):
        if hasattr(args, key):
            setattr(config, key, getattr(args, key))
    return config

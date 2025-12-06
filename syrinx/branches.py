from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Dict
from os.path import isfile, join, abspath
from datetime import datetime
if TYPE_CHECKING:
    pass

def read_branches(root_dir: str) -> Branches:
    cfg_fpath = join(abspath(root_dir), 'syrinx.cfg')
    branches = dict()
    if isfile(cfg_fpath):
        with open(cfg_fpath) as fhandle:
            content = fhandle.read()
            for line in content.splitlines():
                if '=' not in line:
                    continue
                branch, dt, *_ = [p.strip() for p in line.split('=')]
                branches[branch] = dt
    return Branches(branches)

class Branches:
    
    def __init__(self, inner: Dict[str, datetime]) -> None:
        self.inner = inner

    def update(self):
        ## use gitpython to check what the name of the current branch is.
        ## if there is not git or branch, dont do anything
        ## if we do find the branch name, get the update self.inner:
        ## if the branch is in the dict, update it, if its not there add it.
        ##
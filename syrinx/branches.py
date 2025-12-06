from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Dict, Union, Mapping
from os.path import isfile, join, abspath
from datetime import datetime

if TYPE_CHECKING:
    from syrinx.config import BuildMetaInfo

def read_branches(root_dir: str) -> Branches:
    """Read branch information from branches.toml file.
    
    Reads a TOML-formatted file containing branch names and their associated
    datetime values. Each line should be in the format: branch_name = datetime_string
    
    Args:
        root_dir: The root directory where branches.toml is located
        
    Returns:
        A Branches object containing a dictionary mapping branch names to datetime objects
    """
    cfg_fpath = join(abspath(root_dir), 'branches.toml')
    branches = dict()
    if isfile(cfg_fpath):
        with open(cfg_fpath) as fhandle:
            content = fhandle.read()
            for line in content.splitlines():
                if '=' not in line:
                    continue
                branch, dt_str, *_ = [p.strip() for p in line.split('=')]
                # Convert the datetime string to datetime object
                branches[branch] = datetime.fromisoformat(dt_str)
    return Branches(branches)

def write_branches(branches: Dict[str, datetime], root_dir: str) -> None:
    """Write branch information to branches.toml file.
    
    Writes branch names and their associated datetime values to a TOML-formatted file.
    Each branch is written on a separate line in the format: branch_name = datetime_string
    Datetime objects are serialized using ISO 8601 format.
    
    Args:
        branches: Dictionary mapping branch names to datetime objects
        root_dir: The root directory where branches.toml will be created/overwritten
    """
    cfg_fpath = join(abspath(root_dir), 'branches.toml')
    with open(cfg_fpath, 'w') as fhandle:
        for branch, dt in branches.items():
            # Convert datetime to ISO format string
            dt_str = dt.isoformat()
            fhandle.write(f"{branch} = {dt_str}\n")

class Branches:
    
    def __init__(self, inner: Dict[str, datetime]) -> None:
        self.inner = inner

    def update(self, meta: BuildMetaInfo):
        ## use gitpython to check what the name of the current branch is.
        ## if there is not git or branch, dont do anything
        ## if we do find the branch name, get the datetime for this build from meta, 
        ## and update self.inner:
        ## if the branch is in the dict, update it, if its not there add it.
        pass

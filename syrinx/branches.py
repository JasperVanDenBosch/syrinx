from __future__ import annotations
from typing import TYPE_CHECKING, Dict
from os.path import isfile, join, abspath
from datetime import datetime
import logging
from git import Repo, InvalidGitRepositoryError
if TYPE_CHECKING:
    from syrinx.config import BuildMetaInfo
logger = logging.getLogger(__name__)

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
    if branches:
        logger.info(f'Found branches file with {len(branches)} branch')
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

    def update(self, meta: BuildMetaInfo, root_dir: str) -> None:
        """Update branch information with current build metadata.
        
        Uses git to determine the current branch name and records the build timestamp
        for that branch. If no branch is found, does nothing.
        Updates the internal branch dictionary and persists changes to branches.toml.
        
        Args:
            meta: BuildMetaInfo object containing timestamp and other build metadata
            root_dir: The root directory where branches.toml will be written
        """
        try:
            # Try to get the current branch name
            repo = Repo(root_dir, search_parent_directories=True)
            if repo.head.is_detached:
                # Detached HEAD state, no branch name available
                return
            branch_name = repo.active_branch.name
        except (InvalidGitRepositoryError, ValueError, TypeError):
            # Not a git repository or unable to determine branch
            return
        
        # Update the branch with the current build timestamp
        self.inner[branch_name] = meta.timestamp

        logger.info(f'Current branch: {branch_name}. Updating branches file.')
        
        # Write the updated branches to file if we have any entries
        if self.inner:
            write_branches(self.inner, root_dir)

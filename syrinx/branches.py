from __future__ import annotations
from typing import TYPE_CHECKING, Dict
from os.path import isfile, join, abspath
from datetime import datetime
import logging
from git import Repo, InvalidGitRepositoryError
from git import BadName
from syrinx.exceptions import UnknownBranchError
if TYPE_CHECKING:
    from syrinx.config import BuildMetaInfo
    from syrinx.node import ContentNode
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
        self.active = None
        self.changed_files = set()

    def get_lastmodified(self, branch_name: str) -> datetime:
        """Get the last modified datetime for a specific branch.
        
        Args:
            branch_name: The name of the branch to look up
            
        Returns:
            The datetime object associated with the branch
            
        Raises:
            UnknownBranchError: If the branch is not found in self.inner
        """
        if branch_name not in self.inner:
            raise UnknownBranchError(
                f"Branch '{branch_name}' not found in branches data. "
                f"This may indicate that the branches.toml file is missing "
                f"or the branch entry is missing from the file."
            )
        return self.inner[branch_name]

    def update(self, meta: BuildMetaInfo, root_dir: str) -> None:
        """Update branch information with current build metadata.
        
        Uses git to determine the current branch name and records the build timestamp
        for that branch. If no branch is found, does nothing.
        Updates the internal branch dictionary and persists changes to branches.toml.
        Also caches the list of changed files for use in warnIfModifiedNodeHasOutdatedBranch.
        
        Args:
            meta: BuildMetaInfo object containing timestamp and other build metadata
            root_dir: The root directory where branches.toml will be written
        """
        # Convert root_dir to absolute path
        root_dir = abspath(root_dir)
        
        try:
            # Try to get the current branch name
            repo = Repo(root_dir, search_parent_directories=True)
            if repo.head.is_detached:
                # Detached HEAD state, no branch name available
                return
            branch_name = repo.active_branch.name
            
            # Cache changed files (both staged and unstaged, plus untracked)
            # Convert all paths to absolute paths
            try:
                repo_root = abspath(repo.working_dir)
                self.changed_files = set(join(repo_root, f) for f in repo.untracked_files)
                self.changed_files.update(join(repo_root, item.a_path) for item in repo.index.diff(None) if item.a_path)
                self.changed_files.update(join(repo_root, item.a_path) for item in repo.index.diff('HEAD') if item.a_path)
            except (AttributeError, TypeError):
                # Unable to get changed files (e.g., in tests with mocked repo)
                self.changed_files = set()
            
        except (InvalidGitRepositoryError, ValueError, TypeError, BadName):
            # Not a git repository or unable to determine branch
            return
        self.active = branch_name
        
        # Update the branch with the current build timestamp
        self.inner[branch_name] = meta.timestamp

        logger.info(f'Current branch: {branch_name}. Updating branches file.')
        
        # Write the updated branches to file if we have any entries
        if self.inner:
            write_branches(self.inner, root_dir)

    def warnIfModifiedNodeHasOutdatedBranch(self, node: ContentNode, branch: str):
        """Check if a modified node's file has uncommitted changes on a different branch.
        
        If the node's file has uncommitted changes and the specified branch doesn't
        match the currently active branch, logs a warning.
        Uses cached changed_files populated by update() for efficiency.
        
        Args:
            node: The ContentNode to check
            branch: The branch name specified in the node's LastModifiedBranch
        """
        # Only check if we have an active branch to compare against
        if self.active is None:
            return
        
        # If the branch matches the active branch, no warning needed
        if branch == self.active:
            return
        
        source_path_clean = node.source_path.lstrip('/')
        file_path = abspath(join(node.meta.root_dir, 'content', source_path_clean))
        
        # Check if the file is in the cached changed files
        if file_path in self.changed_files:
            logger.warning(
                f"File '{file_path}' has uncommitted changes "
                f"but references LastModifiedBranch '{branch}' while currently on branch '{self.active}'"
            )

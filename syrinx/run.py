from argparse import Namespace
from syrinx.build import build
from syrinx.read import read
from syrinx.preprocess import preprocess
from syrinx.config import configure


def run_pipeline(root_dir: str, args: Namespace):
    """Execute the full build pipeline.
    
    Args:
        root_dir: Root directory to build from
        args: Command-line arguments
    
    Returns:
        The root ContentNode
    """
    
    config = configure(args)
    preprocess(root_dir, config)
    root = read(root_dir, config)
    build(root, root_dir, config)
    return root

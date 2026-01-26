from argparse import Namespace
from os.path import abspath, isdir
from syrinx.build import build
from syrinx.read import read
from syrinx.preprocess import preprocess
from syrinx.config import configure


def run_pipeline(args: Namespace):
    """Execute the full build pipeline.
    
    Args:
        root_dir: Root directory to build from
        args: Command-line arguments
    
    Returns:
        The root ContentNode
    """
    root_dir = abspath(args.dir)
    assert isdir(root_dir)
    config = configure(args)
    preprocess(root_dir, config)
    root = read(root_dir, config)
    build(root, root_dir, config)
    return root

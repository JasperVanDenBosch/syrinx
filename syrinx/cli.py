from syrinx.build import build
from syrinx.read import read
from syrinx.preprocess import preprocess
from os.path import abspath, isdir
import argparse
import logging
from datetime import datetime, UTC
from importlib.metadata import version


class BuildMetaInfo:

    def __init__(self, environment: str) -> None:
        self.environment = environment
        self.timestamp = datetime.now(tz=UTC)
        self.syrinx_version = version('syrinx')


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('root_dir', type=str, help='Location of root directory to build from')
    parser.add_argument('-c', '--clean', action='store_true', 
                        help='Remove existing dynamic content files')
    parser.add_argument('-e', '--environment', default='default', 
                        help='Define build environment for customization, e.g. "production"')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='Print log messages during build')
    return parser.parse_args()

def main():
    args = get_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    root_dir = abspath(args.root_dir)
    assert isdir(root_dir)
    preprocess(root_dir, clean=args.clean)
    
    root = read(root_dir, BuildMetaInfo(args.environment))
    build(root, root_dir)
    print('done.')


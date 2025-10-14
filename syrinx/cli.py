from syrinx.build import build
from syrinx.read import read
from syrinx.preprocess import preprocess
from syrinx.config import configure
from os.path import abspath, isdir
from argparse import ArgumentParser, SUPPRESS
import logging


def get_args():
    parser = ArgumentParser()

    parser.add_argument('root_dir', type=str, help='Location of root directory to build from')
    parser.add_argument('-c', '--clean', default=SUPPRESS, action='store_true',
                        help='Remove existing dynamic content files')
    parser.add_argument('-e', '--environment', default=SUPPRESS, 
                        help='Define build environment for customization, e.g. "production"')
    parser.add_argument('--leaf-pages', default=SUPPRESS, action='store_true',
                        help='Build pages for "leaf" (non-index) content nodes')
    parser.add_argument('-v', '--verbose', default=SUPPRESS, action='store_true', 
                        help='Print log messages during build')
    return parser.parse_args()

def main():
    args = get_args()

    config = configure(args)

    if config.verbose:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        logger.info('Configuration:\n'+str(config))

    root_dir = abspath(args.root_dir)
    assert isdir(root_dir)
    preprocess(root_dir, config)
    
    root = read(root_dir, config)
    build(root, root_dir, config)
    print('done.')


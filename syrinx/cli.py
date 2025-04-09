from syrinx.build import build
from syrinx.read import read
from syrinx.preprocess import preprocess
from os.path import abspath, isdir
import argparse


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("root_dir", type=str, help="Location of root directory to build from")

    return parser.parse_args()

def main():
    args = get_args()

    root_dir = abspath(args.root_dir)
    assert isdir(root_dir)
    preprocess(root_dir)
    root = read(root_dir)
    build(root, root_dir)
    print('done.')

from syrinx.build import build
from syrinx.read import read
from os.path import abspath, isdir
import sys


def main():
    root_dir = abspath(sys.argv[1])
    assert isdir(root_dir)
    root = read(root_dir)
    build(root, root_dir)
    print('done.')

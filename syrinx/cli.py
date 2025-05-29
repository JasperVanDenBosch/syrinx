from syrinx.build import build
from syrinx.read import read
from syrinx.preprocess import preprocess
from os.path import abspath, isdir
import argparse


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("root_dir", type=str, help="Location of root directory to build from")
    parser.add_argument("-c", "--clean", action="store_true", 
                        help="Remove existing dynamic content files")
    parser.add_argument("--dev", action="store_true",
                        help="Run in development mode with live reload")
    parser.add_argument("--port", type=int, default=8000,
                        help="Port for development server (default: 8000)")

    return parser.parse_args()

def main():
    args = get_args()

    root_dir = abspath(args.root_dir)
    assert isdir(root_dir)
    
    if args.dev:
        from syrinx.dev_server import DevServer
        server = DevServer(root_dir, port=args.port)
        server.start()
    else:
        preprocess(root_dir, clean=args.clean)
        root = read(root_dir)
        build(root, root_dir)
        print('done.')

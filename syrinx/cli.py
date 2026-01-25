from syrinx.build import build
from syrinx.read import read
from syrinx.preprocess import preprocess
from syrinx.config import configure
from os.path import abspath, isdir
from argparse import ArgumentParser, SUPPRESS


def get_args():
    """_summary_


    ```
    syrinx
    syrinx build --dir meta
    syrinx serve --dir meta
    ```
    """

    ## Shared arguments
    base_parser = ArgumentParser(add_help=False)
    base_parser.add_argument('-d', '--dir', type=str, default='.', help='Location of root directory to build from')
    base_parser.add_argument('-c', '--clean', default=SUPPRESS, action='store_true',
                        help='Remove existing dynamic content files')
    base_parser.add_argument('-e', '--environment', default=SUPPRESS, 
                        help='Define build environment for customization, e.g. "production"')
    base_parser.add_argument('--leaf-pages', default=SUPPRESS, action='store_true',
                        help='Build pages for "leaf" (non-index) content nodes')
    base_parser.add_argument('-v', '--verbose', default=SUPPRESS, action='store_true', 
                        help='Print log messages during build')

    # top level object
    root_parser = ArgumentParser()
    sub_parsers = root_parser.add_subparsers(
        title='Subcommands ("syrinx . <command> --help" for help for the specific command)')

    ## This adds the "build" sub-command
    build_parser = sub_parsers.add_parser('build', help='Generate html docs', parents=[base_parser])
    build_parser.set_defaults(command='build')

    ## This adds the "serve" sub-command
    serve_parser = sub_parsers.add_parser('serve', help='Serve the generated docs', parents=[base_parser])
    serve_parser.set_defaults(command='serve')
    serve_parser.add_argument('-p', '--port', type=int, default=8000, 
        help='Which port to run the server on')

    return root_parser.parse_args()

def main():
    args = get_args()
    print(args)

    root_dir = abspath(args.dir)
    assert isdir(root_dir)

    config = configure(args)

    if args.command == 'serve':
        from syrinx.dev_server import DevServer
        server = DevServer(root_dir, port=args.port)
        server.start()
        return


    preprocess(root_dir, config)
    
    root = read(root_dir, config)
    build(root, root_dir, config)
    print('done.')



from argparse import ArgumentParser, SUPPRESS
from syrinx.run import run_pipeline
from syrinx.scaffold import generate_scaffold
from syrinx.server.dev_server import DevServer


def get_args():
    """Use ArgumentParser to interpret CLI arguments and return an object with parsed settings.


    ```
    syrinx --help
    syrinx build
    syrinx build --dir meta
    syrinx serve --dir meta
    syrinx new --dir my_site
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

    ## Top level parser object
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
    
    ## This adds the "new" sub-command
    new_parser = sub_parsers.add_parser('new', help='Generate starter site', parents=[base_parser])
    new_parser.set_defaults(command='new')
    new_parser.add_argument('-s', '--scaffold', type=str, default='blog-webawesome', 
        help='Which site scaffold to use to initialize your site')
    new_parser.add_argument('-y', '--yes', action='store_true', default=False, 
        help='Do not prompt for values, just use defaults')

    return root_parser.parse_args()


def main():
    args = get_args()

    if args.command == 'serve':
        DevServer(args).start()
        return
    
    if args.command == 'new':
        generate_scaffold(args)
        return
    
    run_pipeline(args)


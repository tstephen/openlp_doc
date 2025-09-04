"""
__main__.py
"""
import argparse
from getpass import getpass
from importlib.metadata import version
import logging
import sys

from openlp_doc.constants import APP
from openlp_doc.documenter import Documenter, DocumenterOptions
from openlp_doc.exceptions import OpenLpException

def help(parser):
    print(f'{APP.PACKAGE} {APP.VSN}')
    parser.print_help()

def main():
    '''Main entry point to app'''

    parser = argparse.ArgumentParser(prog="openlp_doc", add_help=False)
    # parser.add_argument("-f", "--force", help="overwrite existing files",
    #     action="store_true")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
        type=int, default=logging.WARNING, required=False)
    parser.add_argument('service_file', help="increase output verbosity",
        type=str)
    args = parser.parse_args()
    print(f"Processing file: {args.service_file}")

    ch = logging.StreamHandler()
    ch.setLevel(args.verbose)
    logging.basicConfig(level=args.verbose, handlers=[ ch ])

    try:
        documenter = Documenter(DocumenterOptions())
        documenter.render_service(args.service_file)
        sys.exit(0)
    except OpenLpException as e:
        help(parser)
        sys.exit(e.err.value)

# Do it!
if __name__ == "openlp_doc" or __name__ == "__main__":
    main()


"""
__main__.py
Main entry point
"""
import argparse
from getpass import getpass
from importlib.metadata import version
import logging
import sys

from openlp_doc.constants import APP
from openlp_doc.exceptions import OpenLpException

def help(parser):
    print(f'{APP.PACKAGE} {APP.VSN}')
    parser.print_help()

def main():
    '''Main entry point to kpctl'''

    parser = argparse.ArgumentParser(prog="openlp_doc", add_help=False)
    # parser.add_argument("-f", "--force", help="overwrite existing files",
    #     action="store_true")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
        type=int, default=logging.WARNING, required=False)
    parser.add_argument('service_file', help="increase output verbosity",
        type=str, required=True)
    args = parser.parse_args()

    print(f"Processing file: {args.service_file}")

    # create console handler with coloured output
    ch = logging.StreamHandler()
    ch.setLevel(args.verbose)
    # ch.setFormatter(ColorFormatter())
    logging.basicConfig(level=args.verbose, handlers=[ ch ])

    try:
        sys.exit(0)
    except OpenLpException as e:
        help(parser)
        sys.exit(e.err.value)

# Do it!
if __name__ == "kpctl" or __name__ == "__main__":
    main()


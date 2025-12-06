"""
__main__.py for openlp_ctrl
"""

import argparse
import sys

import uvicorn


def help(parser):
    print("OpenLP Control 0.1.0")
    parser.print_help()


def main():
    """Main entry point to openlp_ctrl app"""

    parser = argparse.ArgumentParser(prog="openlp_ctrl", add_help=False)
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true",
        default=False,
        required=False,
    )
    parser.add_argument(
        "--version",
        help="show version",
        action="store_true",
        default=False,
        required=False,
    )
    parser.add_argument(
        "--host",
        help="host to bind to",
        type=str,
        default="127.0.0.1",
        required=False,
    )
    parser.add_argument(
        "--port",
        help="port to bind to",
        type=int,
        default=8000,
        required=False,
    )

    args = parser.parse_args()

    if args.version:
        print("OpenLP Control 0.1.0")
        sys.exit(0)

    # Set up logging
    log_level = "debug" if args.verbose else "info"

    print(f"Starting OpenLP Control server on {args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")

    # Set server configuration for template rendering
    import os

    from .server import set_server_config

    # Read server URL from environment variable if set
    server_url = os.getenv("SERVER_URL")
    if server_url:  # useful for k8s deployment
        set_server_config(server_url)
    else:  # usefulf for local testing
        set_server_config(f"http://{args.host}:{args.port}")

    try:
        uvicorn.run(
            "openlp_ctrl.server:app",
            host=args.host,
            port=args.port,
            log_level=log_level,
            reload=False,
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


# Do it!
if __name__ == "openlp_ctrl" or __name__ == "__main__":
    main()

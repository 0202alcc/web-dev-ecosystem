import argparse
from app import create_app


def create_parser():
    parser = argparse.ArgumentParser(description="Run Flask WebPush application")
    parser.add_argument(
        "--port",
        type=int,
        default=3000,
        help="Port to run the server on (default: 3000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to run the server on (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=True,
        help="Run in debug mode (default: True)",
    )
    return parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)

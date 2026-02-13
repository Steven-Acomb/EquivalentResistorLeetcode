"""CLI entry point: python -m server"""

import argparse

import uvicorn


def main():
    parser = argparse.ArgumentParser(
        prog="server",
        description="Start the local problem workbench",
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to listen on (default: 8000)",
    )
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)",
    )

    args = parser.parse_args()

    print(f"Starting workbench at http://{args.host}:{args.port}")
    uvicorn.run("server.app:app", host=args.host, port=args.port)


if __name__ == "__main__":
    main()

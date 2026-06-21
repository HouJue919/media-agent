from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote


DEFAULT_PORT = 8000
DEFAULT_REPORT = "video_report.html"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Serve Media Agent HTML reports over local HTTP.")
    parser.add_argument(
        "--directory",
        default=".",
        help="Directory to serve. Defaults to the current directory.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Local HTTP port. Defaults to {DEFAULT_PORT}.",
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host interface to bind. Defaults to localhost.",
    )
    parser.add_argument(
        "--report",
        default=DEFAULT_REPORT,
        help=f"Report file name or relative path to print in the preview URL. Defaults to {DEFAULT_REPORT}.",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def build_report_url(host: str, port: int, report: str) -> str:
    report_path = quote(report.lstrip("/"))
    return f"http://{host}:{port}/{report_path}"


def serve(directory: Path, host: str, port: int, report: str) -> None:
    resolved_directory = directory.expanduser().resolve()
    if not resolved_directory.exists():
        raise FileNotFoundError(f"Directory does not exist: {resolved_directory}")
    if not resolved_directory.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {resolved_directory}")

    handler = partial(SimpleHTTPRequestHandler, directory=str(resolved_directory))
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Serving directory: {resolved_directory}")
    print(f"Directory URL: http://{host}:{port}/")
    print(f"Report URL: {build_report_url(host, port, report)}")
    print("Press Ctrl+C to stop the preview server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping preview server.")
    finally:
        server.server_close()


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    serve(Path(args.directory), args.host, args.port, args.report)


if __name__ == "__main__":
    main()

from __future__ import annotations

import subprocess
import sys

from scripts import serve_report


def test_serve_report_default_args() -> None:
    args = serve_report.parse_args([])

    assert args.directory == "."
    assert args.port == 8000
    assert args.host == "localhost"
    assert args.report == "video_report.html"


def test_serve_report_custom_args() -> None:
    args = serve_report.parse_args(
        [
            "--directory",
            "test_outputs/video_report",
            "--port",
            "8123",
            "--host",
            "127.0.0.1",
            "--report",
            "nested/report.html",
        ]
    )

    assert args.directory == "test_outputs/video_report"
    assert args.port == 8123
    assert args.host == "127.0.0.1"
    assert args.report == "nested/report.html"
    assert serve_report.build_report_url(args.host, args.port, args.report) == "http://127.0.0.1:8123/nested/report.html"


def test_serve_report_help_runs() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/serve_report.py", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "--directory" in completed.stdout
    assert "--port" in completed.stdout

from __future__ import annotations

import py_compile
import sys
from pathlib import Path

import app


def test_app_py_exists_and_compiles() -> None:
    app_path = Path("app.py")
    assert app_path.exists()
    py_compile.compile(str(app_path), doraise=True)


def test_build_photo_command() -> None:
    command = app.build_photo_command(
        "demo_media",
        language="en",
        report="demo_report.html",
        output="media_index.csv",
        enable_ai_tags=True,
        python_executable="python",
    )

    assert command == [
        "python",
        str(app.PROJECT_ROOT / "main.py"),
        "demo_media",
        "--mode",
        "photo",
        "--language",
        "en",
        "--report",
        "demo_report.html",
        "--output",
        "media_index.csv",
        "--enable-ai-tags",
        "--ai-provider",
        "mock",
    ]


def test_build_video_command() -> None:
    command = app.build_video_command(
        "demo_videos",
        language="zh",
        report="video_report_zh.html",
        output="video_index.csv",
        frame_interval=3,
        max_frames=8,
        python_executable=sys.executable,
    )

    assert command == [
        sys.executable,
        str(app.PROJECT_ROOT / "main.py"),
        "demo_videos",
        "--mode",
        "video",
        "--language",
        "zh",
        "--report",
        "video_report_zh.html",
        "--output",
        "video_index.csv",
        "--frame-interval",
        "3",
        "--max-frames",
        "8",
    ]


def test_build_organize_commands() -> None:
    photo_command = app.build_photo_organize_command(
        "decisions.csv",
        organize_output="organized_media",
        organize_mode="copy",
        python_executable="python",
    )
    video_command = app.build_video_organize_command(
        "video_decisions.csv",
        organize_output="organized_videos",
        organize_mode="copy",
        python_executable="python",
    )

    assert photo_command == [
        "python",
        str(app.PROJECT_ROOT / "main.py"),
        "--decisions",
        "decisions.csv",
        "--organize-output",
        "organized_media",
        "--organize-mode",
        "copy",
    ]
    assert video_command == [
        "python",
        str(app.PROJECT_ROOT / "main.py"),
        "--mode",
        "video-organize",
        "--video-decisions",
        "video_decisions.csv",
        "--video-organize-output",
        "organized_videos",
        "--mode-action",
        "copy",
    ]


def test_parse_cli_output() -> None:
    output = "\n".join(
        [
            "Scanned 3 media files.",
            "CSV written to: /tmp/media_index.csv",
            "Thumbnails written to: /tmp/thumbnails",
            "HTML report written to: /tmp/report.html",
        ]
    )

    result = app.parse_cli_output(output)

    assert result["scanned"] == "Scanned 3 media files."
    assert result["csv_path"] == "/tmp/media_index.csv"
    assert result["thumbnails_path"] == "/tmp/thumbnails"
    assert result["report_path"] == "/tmp/report.html"

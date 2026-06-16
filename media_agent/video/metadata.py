from __future__ import annotations

import json
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any


def ffprobe_available() -> bool:
    return shutil.which("ffprobe") is not None


def read_video_metadata(path: Path) -> dict[str, Any]:
    if not ffprobe_available():
        raise RuntimeError("ffprobe is required for video metadata. Install ffmpeg and make ffprobe available on PATH.")

    stat = path.stat()
    probe = _run_ffprobe(path)
    format_data = probe.get("format") or {}
    streams = probe.get("streams") or []
    video_stream = _first_video_stream(streams)

    duration = _to_float(video_stream.get("duration")) if video_stream else None
    if duration is None:
        duration = _to_float(format_data.get("duration"))

    return {
        "filename": path.name,
        "file_path": str(path),
        "file_size": stat.st_size,
        "duration_seconds": _round_or_none(duration),
        "width": _to_int(video_stream.get("width")) if video_stream else None,
        "height": _to_int(video_stream.get("height")) if video_stream else None,
        "fps": _parse_frame_rate(
            video_stream.get("avg_frame_rate") or video_stream.get("r_frame_rate") if video_stream else None
        ),
        "codec": video_stream.get("codec_name") if video_stream else None,
        "created_time": _created_time(format_data, video_stream),
    }


def _run_ffprobe(path: Path) -> dict[str, Any]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        message = completed.stderr.strip() or "unknown ffprobe error"
        raise RuntimeError(f"ffprobe failed for {path}: {message}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"ffprobe returned invalid JSON for {path}") from exc


def _first_video_stream(streams: list[dict[str, Any]]) -> dict[str, Any] | None:
    for stream in streams:
        if stream.get("codec_type") == "video":
            return stream
    return None


def _created_time(format_data: dict[str, Any], video_stream: dict[str, Any] | None) -> str | None:
    stream_tags = (video_stream or {}).get("tags") or {}
    format_tags = format_data.get("tags") or {}
    return stream_tags.get("creation_time") or format_tags.get("creation_time")


def _parse_frame_rate(value: Any) -> float | None:
    if value in (None, "", "0/0"):
        return None
    try:
        parsed = float(Fraction(str(value)))
    except (ValueError, ZeroDivisionError):
        return None
    return round(parsed, 3)


def _round_or_none(value: float | None) -> float | None:
    return round(value, 3) if value is not None else None


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

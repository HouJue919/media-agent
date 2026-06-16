from __future__ import annotations

from pathlib import Path


SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v"}


def is_supported_video(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in SUPPORTED_VIDEO_EXTENSIONS


def scan_video_files(folder: Path, recursive: bool = True) -> list[Path]:
    pattern = "**/*" if recursive else "*"
    return sorted(
        (path for path in folder.glob(pattern) if is_supported_video(path)),
        key=lambda item: str(item).lower(),
    )

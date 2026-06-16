from __future__ import annotations

from pathlib import Path

from media_agent.video.scanner import scan_video_files


def test_video_scanner_recognizes_supported_video_extensions(tmp_path: Path) -> None:
    supported_names = [
        "one.mp4",
        "two.mov",
        "three.m4v",
    ]
    for name in supported_names:
        (tmp_path / name).write_bytes(b"demo")
    (tmp_path / ".DS_Store").write_bytes(b"metadata")
    (tmp_path / "notes.txt").write_text("ignore me", encoding="utf-8")
    (tmp_path / "photo.jpg").write_bytes(b"not a video")

    scanned = scan_video_files(tmp_path)

    assert {path.name for path in scanned} == set(supported_names)


def test_video_scanner_can_disable_recursive_scanning(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    (tmp_path / "root.mp4").write_bytes(b"demo")
    (nested / "nested.mp4").write_bytes(b"demo")

    scanned = scan_video_files(tmp_path, recursive=False)

    assert [path.name for path in scanned] == ["root.mp4"]

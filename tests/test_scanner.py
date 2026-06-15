from __future__ import annotations

from pathlib import Path

from media_agent.scanner import scan_media_files


def test_scanner_recognizes_supported_image_extensions(tmp_path: Path) -> None:
    supported_names = [
        "one.jpg",
        "two.jpeg",
        "three.png",
        "four.heic",
        "five.arw",
    ]
    for name in supported_names:
        (tmp_path / name).write_bytes(b"demo")
    (tmp_path / ".DS_Store").write_bytes(b"metadata")
    (tmp_path / "notes.txt").write_text("ignore me", encoding="utf-8")

    scanned = scan_media_files(tmp_path)

    assert {path.name for path in scanned} == set(supported_names)


def test_scanner_can_disable_recursive_scanning(tmp_path: Path) -> None:
    nested = tmp_path / "nested"
    nested.mkdir()
    (tmp_path / "root.jpg").write_bytes(b"demo")
    (nested / "nested.jpg").write_bytes(b"demo")

    scanned = scan_media_files(tmp_path, recursive=False)

    assert [path.name for path in scanned] == ["root.jpg"]

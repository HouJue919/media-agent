from __future__ import annotations

import py_compile
from pathlib import Path

from scripts import create_desktop_launcher


def test_create_desktop_launcher_compiles() -> None:
    py_compile.compile("scripts/create_desktop_launcher.py", doraise=True)


def test_launcher_content_contains_required_commands_and_notices() -> None:
    content = create_desktop_launcher.build_launcher_content()

    assert "streamlit run app.py" in content
    assert "/Users/adanhou/Documents/素材筛选ai" in content
    assert "Media Agent GUI" in content
    assert "Local photo and video asset management for creators." in content
    assert "All processing runs locally. Media files are not uploaded." in content
    assert "pip install -r requirements-gui.txt" in content


def test_create_launcher_writes_executable_command_file(tmp_path: Path) -> None:
    launcher_path = create_desktop_launcher.create_launcher(desktop_dir=tmp_path)

    assert launcher_path.name == "Media Agent GUI.command"
    assert launcher_path.exists()
    assert launcher_path.stat().st_mode & 0o111
    assert "streamlit run app.py" in launcher_path.read_text(encoding="utf-8")

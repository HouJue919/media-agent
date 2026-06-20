from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from media_agent.video import keyframes


def test_keyframe_extraction_falls_back_to_first_frame_for_short_videos(monkeypatch, tmp_path: Path) -> None:
    commands: list[list[str]] = []

    def fake_run(command: list[str], capture_output: bool, text: bool, check: bool) -> SimpleNamespace:
        commands.append(command)
        if "-frames:v" in command and command[command.index("-frames:v") + 1] == "1":
            Path(command[-1]).write_bytes(b"demo frame")
        return SimpleNamespace(returncode=0, stderr="")

    monkeypatch.setattr(keyframes, "ffmpeg_available", lambda: True)
    monkeypatch.setattr(keyframes.subprocess, "run", fake_run)

    frame_paths = keyframes.extract_keyframes(Path("short_demo.mp4"), tmp_path, interval_seconds=5, max_frames=12)

    assert frame_paths == [tmp_path / "short_demo" / "frame_001.jpg"]
    assert len(commands) == 2
    assert "fps=1/5" in commands[0]
    assert commands[1][commands[1].index("-frames:v") + 1] == "1"

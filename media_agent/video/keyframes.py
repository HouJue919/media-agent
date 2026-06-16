from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def extract_keyframes(
    video_path: Path,
    output_root: Path,
    interval_seconds: float = 5.0,
    max_frames: int = 12,
) -> list[Path]:
    if interval_seconds <= 0:
        raise ValueError("--frame-interval must be greater than 0.")
    if max_frames <= 0:
        raise ValueError("--max-frames must be greater than 0.")
    if not ffmpeg_available():
        raise RuntimeError("ffmpeg is required for video keyframe extraction. Install ffmpeg and make it available on PATH.")

    output_dir = output_root / video_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    output_pattern = output_dir / "frame_%03d.jpg"
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(video_path),
        "-vf",
        f"fps=1/{interval_seconds}",
        "-frames:v",
        str(max_frames),
        "-q:v",
        "2",
        str(output_pattern),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        message = completed.stderr.strip() or "unknown ffmpeg error"
        raise RuntimeError(f"ffmpeg failed for {video_path}: {message}")

    return [
        output_dir / f"frame_{index:03d}.jpg"
        for index in range(1, max_frames + 1)
        if (output_dir / f"frame_{index:03d}.jpg").exists()
    ]

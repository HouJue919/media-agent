from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEMO_VIDEO_DIR = PROJECT_ROOT / "demo_videos"


def main() -> None:
    if shutil.which("ffmpeg") is None:
        print("ffmpeg is not available. Skipping demo video generation.")
        print("Install ffmpeg to generate synthetic demo videos locally.")
        return

    DEMO_VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    _generate_video(
        DEMO_VIDEO_DIR / "sharp_normal_demo.mp4",
        "testsrc2=size=640x360:rate=24:duration=6",
    )
    _generate_video(
        DEMO_VIDEO_DIR / "dark_blurry_demo.mp4",
        "testsrc2=size=640x360:rate=24:duration=6,boxblur=10:1,eq=brightness=-0.45",
    )
    _generate_video(
        DEMO_VIDEO_DIR / "bright_overexposed_demo.mp4",
        "testsrc2=size=640x360:rate=24:duration=6,eq=brightness=0.65:contrast=0.7",
    )
    print(f"Generated synthetic demo videos in: {DEMO_VIDEO_DIR}")


def _generate_video(output_path: Path, filter_graph: str) -> None:
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "lavfi",
        "-i",
        filter_graph,
        "-t",
        "6",
        "-pix_fmt",
        "yuv420p",
        str(output_path),
    ]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()

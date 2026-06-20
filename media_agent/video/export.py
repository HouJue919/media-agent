from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


VIDEO_CSV_FIELDS = [
    "filename",
    "file_path",
    "file_size",
    "duration_seconds",
    "width",
    "height",
    "fps",
    "codec",
    "created_time",
    "frame_count",
    "keyframe_dir",
    "avg_blur_score",
    "min_blur_score",
    "avg_exposure_score",
    "overexposed_frame_count",
    "underexposed_frame_count",
    "blurry_frame_count",
    "stability_score",
    "avg_motion",
    "max_motion",
    "shaky_frame_count",
    "stability_recommendation",
    "video_quality_recommendation",
    "recommendation_reason",
]


def export_video_csv(records: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=VIDEO_CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

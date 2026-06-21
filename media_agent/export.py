from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


CSV_FIELDS = [
    "filename",
    "path",
    "file_size_bytes",
    "created_at",
    "modified_at",
    "width",
    "height",
    "camera_model",
    "lens_model",
    "focal_length",
    "aperture",
    "shutter_speed",
    "iso",
    "taken_at",
    "thumbnail_path",
    "face_detected",
    "face_count",
    "person_signal",
    "person_signal_confidence",
    "person_signal_method",
    "phash",
    "duplicate_group_id",
    "duplicate_count",
    "is_duplicate_candidate",
    "group_best_pick",
    "group_rank",
    "technical_recommendation",
    "final_recommendation",
    "keep_recommendation",
    "recommendation_reason",
    "memory_risk",
    "memory_risk_reason",
    "content_safety_override",
    "ai_description",
    "ai_tags",
    "scene_type",
    "subject_type",
    "suggested_use",
    "ai_confidence",
    "ai_provider",
    "exposure_score",
    "overexposed_ratio",
    "underexposed_ratio",
    "blur_score",
    "is_blurry",
    "waste_candidate",
    "quality_error",
]


def export_csv(records: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

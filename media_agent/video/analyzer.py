from __future__ import annotations

from pathlib import Path
from typing import Any

from media_agent.quality import analyze_quality


SEVERE_BLUR_THRESHOLD = 80.0
KEEP_BLUR_THRESHOLD = 220.0
SEVERE_EXPOSURE_SCORE = 45.0
KEEP_EXPOSURE_THRESHOLD = 85.0
SEVERE_OVEREXPOSED_RATIO = 0.20
SEVERE_UNDEREXPOSED_RATIO = 0.30


def analyze_video_keyframes(frame_paths: list[Path]) -> dict[str, Any]:
    frame_results = [analyze_quality(path) for path in frame_paths]
    frame_count = len(frame_results)

    blur_scores = [_number_or_none(result.get("blur_score")) for result in frame_results]
    exposure_scores = [_number_or_none(result.get("exposure_score")) for result in frame_results]
    blur_scores = [score for score in blur_scores if score is not None]
    exposure_scores = [score for score in exposure_scores if score is not None]

    overexposed_frame_count = sum(
        1 for result in frame_results if _number_or_default(result.get("overexposed_ratio"), 0.0) >= SEVERE_OVEREXPOSED_RATIO
    )
    underexposed_frame_count = sum(
        1
        for result in frame_results
        if _number_or_default(result.get("underexposed_ratio"), 0.0) >= SEVERE_UNDEREXPOSED_RATIO
    )
    blurry_frame_count = sum(
        1
        for result in frame_results
        if result.get("is_blurry") is True or _number_or_default(result.get("blur_score"), float("inf")) < SEVERE_BLUR_THRESHOLD
    )

    summary = {
        "avg_blur_score": _round_or_none(_average(blur_scores)),
        "min_blur_score": _round_or_none(min(blur_scores) if blur_scores else None),
        "avg_exposure_score": _round_or_none(_average(exposure_scores)),
        "overexposed_frame_count": overexposed_frame_count,
        "underexposed_frame_count": underexposed_frame_count,
        "blurry_frame_count": blurry_frame_count,
        "frame_count": frame_count,
    }
    recommendation, reason = _recommend_video(summary)
    summary["video_quality_recommendation"] = recommendation
    summary["recommendation_reason"] = reason
    return summary


def _recommend_video(summary: dict[str, Any]) -> tuple[str, str]:
    frame_count = int(summary.get("frame_count") or 0)
    if frame_count == 0:
        return "review", "no keyframes extracted"

    issue_count = max(
        int(summary.get("blurry_frame_count") or 0),
        int(summary.get("overexposed_frame_count") or 0),
        int(summary.get("underexposed_frame_count") or 0),
    )
    avg_blur = _number_or_default(summary.get("avg_blur_score"), 0.0)
    min_blur = _number_or_default(summary.get("min_blur_score"), 0.0)
    avg_exposure = _number_or_default(summary.get("avg_exposure_score"), 0.0)

    if issue_count > frame_count / 2 or avg_exposure < SEVERE_EXPOSURE_SCORE:
        return "reject_candidate", "majority keyframes have severe blur or exposure issues"
    if avg_blur >= KEEP_BLUR_THRESHOLD and min_blur >= SEVERE_BLUR_THRESHOLD and avg_exposure >= KEEP_EXPOSURE_THRESHOLD:
        return "keep", "clear keyframes, good exposure"
    return "review", "mixed keyframe quality, review needed"


def _average(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _round_or_none(value: float | None) -> float | None:
    return round(value, 2) if value is not None else None


def _number_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _number_or_default(value: Any, default: float) -> float:
    parsed = _number_or_none(value)
    return parsed if parsed is not None else default

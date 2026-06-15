from __future__ import annotations

from collections import defaultdict
from typing import Any


KEEP = "keep"
REVIEW = "review"
REJECT_CANDIDATE = "reject_candidate"

SEVERE_BLUR_THRESHOLD = 80.0
REVIEW_BLUR_THRESHOLD = 220.0
SEVERE_EXPOSURE_SCORE = 45.0
REVIEW_EXPOSURE_SCORE = 85.0
SEVERE_OVEREXPOSED_RATIO = 0.20
REVIEW_OVEREXPOSED_RATIO = 0.03
SEVERE_UNDEREXPOSED_RATIO = 0.30
REVIEW_UNDEREXPOSED_RATIO = 0.08


def annotate_best_picks(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    duplicate_groups = _group_duplicate_records(records)

    for record in records:
        record["group_best_pick"] = False
        record["group_rank"] = None
        recommendation, reason = _recommend_single_record(record)
        record["keep_recommendation"] = recommendation
        record["recommendation_reason"] = reason

    for group_records in duplicate_groups.values():
        ranked_records = sorted(group_records, key=_score_record, reverse=True)
        for rank, record in enumerate(ranked_records, start=1):
            record["group_rank"] = rank
            record["group_best_pick"] = rank == 1
            recommendation, reason = _recommend_duplicate_record(record, rank)
            record["keep_recommendation"] = recommendation
            record["recommendation_reason"] = reason

    return records


def _group_duplicate_records(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        group_id = record.get("duplicate_group_id")
        if group_id:
            groups[str(group_id)].append(record)
    return groups


def _score_record(record: dict[str, Any]) -> tuple[int, float, float, int, str]:
    not_waste = 1 if record.get("waste_candidate") is False else 0
    blur_score = _number_or_default(record.get("blur_score"), -1.0)
    exposure_score = _number_or_default(record.get("exposure_score"), -1.0)
    resolution = _resolution(record)
    filename = str(record.get("filename") or "")
    return (not_waste, blur_score, exposure_score, resolution, filename)


def _recommend_duplicate_record(record: dict[str, Any], rank: int) -> tuple[str, str]:
    if rank != 1:
        return REJECT_CANDIDATE, "duplicate and not best pick"

    recommendation, reason = _quality_recommendation(record)
    if recommendation == KEEP:
        return KEEP, "duplicate but best in group"
    if recommendation == REVIEW:
        return REVIEW, f"duplicate but best in group; {reason}"
    return REJECT_CANDIDATE, reason


def _recommend_single_record(record: dict[str, Any]) -> tuple[str, str]:
    return _quality_recommendation(record)


def _quality_recommendation(record: dict[str, Any]) -> tuple[str, str]:
    if _missing_quality(record):
        return REVIEW, "quality metrics unavailable"

    blur_score = _number_or_default(record.get("blur_score"), -1.0)
    exposure_score = _number_or_default(record.get("exposure_score"), -1.0)
    overexposed_ratio = _number_or_default(record.get("overexposed_ratio"), 0.0)
    underexposed_ratio = _number_or_default(record.get("underexposed_ratio"), 0.0)

    if blur_score < SEVERE_BLUR_THRESHOLD:
        return REJECT_CANDIDATE, "blurry image"
    if overexposed_ratio >= SEVERE_OVEREXPOSED_RATIO:
        return REJECT_CANDIDATE, "overexposed"
    if underexposed_ratio >= SEVERE_UNDEREXPOSED_RATIO:
        return REJECT_CANDIDATE, "underexposed"
    if exposure_score < SEVERE_EXPOSURE_SCORE:
        return REJECT_CANDIDATE, "low quality candidate"

    if blur_score < REVIEW_BLUR_THRESHOLD:
        return REVIEW, "slightly blurry, review needed"
    if overexposed_ratio >= REVIEW_OVEREXPOSED_RATIO:
        return REVIEW, "mild overexposure, review needed"
    if underexposed_ratio >= REVIEW_UNDEREXPOSED_RATIO:
        return REVIEW, "mild underexposure, review needed"
    if exposure_score < REVIEW_EXPOSURE_SCORE:
        return REVIEW, "mild exposure issue, review needed"

    return KEEP, "sharp image, good exposure"


def _missing_quality(record: dict[str, Any]) -> bool:
    return record.get("blur_score") in (None, "") or record.get("exposure_score") in (None, "")


def _resolution(record: dict[str, Any]) -> int:
    width = _int_or_default(record.get("width"), 0)
    height = _int_or_default(record.get("height"), 0)
    return width * height


def _number_or_default(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int_or_default(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

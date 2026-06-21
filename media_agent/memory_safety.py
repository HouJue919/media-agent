from __future__ import annotations

from collections import defaultdict
from typing import Any


KEEP = "keep"
REVIEW = "review"
REJECT_CANDIDATE = "reject_candidate"

MEMORY_KEYWORDS = (
    "person",
    "people",
    "face",
    "selfie",
    "portrait",
    "friend",
    "family",
    "group",
    "memory",
    "birthday",
    "travel",
    "trip",
)
AI_PERSON_KEYWORDS = ("person", "portrait", "people", "face")

SEVERE_BLUR_THRESHOLD = 80.0
SEVERE_EXPOSURE_SCORE = 45.0
SEVERE_OVEREXPOSED_RATIO = 0.20
SEVERE_UNDEREXPOSED_RATIO = 0.30
CLOSE_BLUR_RATIO = 0.65
CLOSE_EXPOSURE_DELTA = 10.0


def apply_memory_safe_recommendations(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best_by_group = _best_records_by_duplicate_group(records)

    for record in records:
        technical_recommendation = str(record.get("technical_recommendation") or record.get("keep_recommendation") or REVIEW)
        original_reason = str(record.get("recommendation_reason") or "")
        memory_risk, memory_reason = _memory_risk(record)
        final_recommendation = technical_recommendation
        content_safety_override = memory_risk == "high"
        reasons = [original_reason] if original_reason else []

        duplicate_override = _duplicate_review_override(record, best_by_group)
        if duplicate_override:
            if memory_risk == "low":
                memory_risk = "medium"
                memory_reason = "duplicate but may contain different expression"
            if final_recommendation == REJECT_CANDIDATE:
                final_recommendation = REVIEW
            content_safety_override = True
            reasons.append("duplicate but may contain different expression or moment")

        if final_recommendation == REJECT_CANDIDATE and memory_risk in {"high", "medium"}:
            final_recommendation = REVIEW
            content_safety_override = True
            reasons.append(_memory_safe_review_reason(record))

        if final_recommendation == KEEP and _content_unknown(record):
            reasons.append("technically good image; content not evaluated")

        if final_recommendation == REJECT_CANDIDATE and memory_risk == "low" and _has_severe_technical_issue(record):
            reasons = [_technical_reject_reason(record)]

        record["technical_recommendation"] = technical_recommendation
        record["final_recommendation"] = final_recommendation
        record["keep_recommendation"] = final_recommendation
        record["memory_risk"] = memory_risk
        record["memory_risk_reason"] = memory_reason
        record["content_safety_override"] = content_safety_override
        record["recommendation_reason"] = _join_reasons(reasons)

    return records


def _memory_risk(record: dict[str, Any]) -> tuple[str, str]:
    path_text = _search_text(record, ("filename", "path"))
    if _contains_any(path_text, MEMORY_KEYWORDS):
        return "high", "possible person or memory photo"

    ai_text = _search_text(record, ("ai_tags", "subject_type", "scene_type", "ai_description"))
    if _contains_any(ai_text, AI_PERSON_KEYWORDS):
        return "high", "possible person or face"

    if _int_or_default(record.get("duplicate_count"), 0) > 1 and record.get("duplicate_group_id"):
        return "medium", "duplicate but may contain different expression"

    if not path_text and not ai_text:
        return "unknown", "no content signal available"
    return "low", "no obvious memory signal"


def _duplicate_review_override(record: dict[str, Any], best_by_group: dict[str, dict[str, Any]]) -> bool:
    group_id = record.get("duplicate_group_id")
    if not group_id or record.get("group_best_pick") is True:
        return False
    best_record = best_by_group.get(str(group_id))
    if not best_record or best_record is record:
        return False
    if str(record.get("technical_recommendation") or record.get("keep_recommendation") or "") != REJECT_CANDIDATE:
        return False
    return _quality_close_to_best(record, best_record)


def _quality_close_to_best(record: dict[str, Any], best_record: dict[str, Any]) -> bool:
    blur_score = _number_or_default(record.get("blur_score"), None)
    best_blur = _number_or_default(best_record.get("blur_score"), None)
    exposure_score = _number_or_default(record.get("exposure_score"), None)
    best_exposure = _number_or_default(best_record.get("exposure_score"), None)

    blur_close = blur_score is not None and best_blur not in (None, 0) and blur_score / best_blur >= CLOSE_BLUR_RATIO
    exposure_close = (
        exposure_score is not None
        and best_exposure is not None
        and abs(exposure_score - best_exposure) <= CLOSE_EXPOSURE_DELTA
        and _number_or_default(record.get("blur_score"), 0.0) >= SEVERE_BLUR_THRESHOLD
    )
    return blur_close or exposure_close


def _best_records_by_duplicate_group(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        group_id = record.get("duplicate_group_id")
        if group_id:
            grouped[str(group_id)].append(record)

    best_by_group = {}
    for group_id, group_records in grouped.items():
        explicit_best = next((record for record in group_records if record.get("group_best_pick") is True), None)
        best_by_group[group_id] = explicit_best or min(group_records, key=lambda record: _int_or_default(record.get("group_rank"), 9999))
    return best_by_group


def _content_unknown(record: dict[str, Any]) -> bool:
    ai_description = str(record.get("ai_description") or "").strip().lower()
    ai_tags = str(record.get("ai_tags") or "").strip()
    return ai_tags == "" and ai_description in {"", "unknown"}


def _has_severe_technical_issue(record: dict[str, Any]) -> bool:
    blur_score = _number_or_default(record.get("blur_score"), 9999.0)
    exposure_score = _number_or_default(record.get("exposure_score"), 100.0)
    overexposed_ratio = _number_or_default(record.get("overexposed_ratio"), 0.0)
    underexposed_ratio = _number_or_default(record.get("underexposed_ratio"), 0.0)
    return (
        blur_score < SEVERE_BLUR_THRESHOLD
        or exposure_score < SEVERE_EXPOSURE_SCORE
        or overexposed_ratio >= SEVERE_OVEREXPOSED_RATIO
        or underexposed_ratio >= SEVERE_UNDEREXPOSED_RATIO
    )


def _technical_reject_reason(record: dict[str, Any]) -> str:
    blur_score = _number_or_default(record.get("blur_score"), 9999.0)
    overexposed_ratio = _number_or_default(record.get("overexposed_ratio"), 0.0)
    underexposed_ratio = _number_or_default(record.get("underexposed_ratio"), 0.0)
    exposure_score = _number_or_default(record.get("exposure_score"), 100.0)
    if blur_score < SEVERE_BLUR_THRESHOLD:
        return "technical reject candidate: severe blur"
    if overexposed_ratio >= SEVERE_OVEREXPOSED_RATIO:
        return "technical reject candidate: severe overexposure"
    if underexposed_ratio >= SEVERE_UNDEREXPOSED_RATIO:
        return "technical reject candidate: severe underexposure"
    if exposure_score < SEVERE_EXPOSURE_SCORE:
        return "technical reject candidate: severe exposure issue"
    return "technical reject candidate: severe blur/exposure issue"


def _memory_safe_review_reason(record: dict[str, Any]) -> str:
    reason = str(record.get("recommendation_reason") or "")
    if "blur" in reason.lower() or _number_or_default(record.get("blur_score"), 9999.0) < SEVERE_BLUR_THRESHOLD:
        return "blurry image; memory-safe review recommended"
    return "technical issue but memory-safe review recommended"


def _join_reasons(reasons: list[str]) -> str:
    cleaned = []
    for reason in reasons:
        reason = reason.strip()
        if reason and reason not in cleaned:
            cleaned.append(reason)
    return "; ".join(cleaned)


def _search_text(record: dict[str, Any], fields: tuple[str, ...]) -> str:
    return " ".join(str(record.get(field) or "").lower() for field in fields if record.get(field) not in (None, ""))


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def _number_or_default(value: Any, default: float | None) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int_or_default(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

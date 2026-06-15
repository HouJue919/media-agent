from __future__ import annotations

import re
from typing import Any


AI_FIELD_NAMES = [
    "ai_description",
    "ai_tags",
    "scene_type",
    "subject_type",
    "suggested_use",
    "ai_confidence",
    "ai_provider",
]


EMPTY_AI_TAGS = {
    "ai_description": "",
    "ai_tags": "",
    "scene_type": "",
    "subject_type": "",
    "suggested_use": "",
    "ai_confidence": "",
    "ai_provider": "",
}


def tag_media_item(item: dict[str, Any]) -> dict[str, Any]:
    text = _search_text(item)
    tags: list[str] = []
    result: dict[str, Any] = {
        "ai_description": "Unknown",
        "ai_tags": "",
        "scene_type": "unknown",
        "subject_type": "unknown",
        "suggested_use": "review_needed",
        "ai_confidence": 0.0,
        "ai_provider": "mock",
    }

    matched = False

    if _has_any(text, ("fuji", "fujisan", "mountain", "mt")):
        matched = True
        _add_tags(tags, ("mountain", "landscape"))
        result.update(
            {
                "ai_description": "Mountain landscape photo",
                "scene_type": "landscape",
                "subject_type": "mountain",
                "suggested_use": "b_roll",
                "ai_confidence": max(float(result["ai_confidence"]), 0.8),
            }
        )

    if _has_any(text, ("sunrise", "sunset", "dawn", "dusk")):
        matched = True
        sky_event = "sunset" if _has_any(text, ("sunset", "dusk")) else "sunrise"
        _add_tags(tags, (sky_event, "sky", "landscape"))
        result.update(
            {
                "ai_description": "Sunrise or sunset landscape photo",
                "scene_type": "landscape",
                "subject_type": "sky",
                "suggested_use": "documentary_opening",
                "ai_confidence": max(float(result["ai_confidence"]), 0.8),
            }
        )

    if _has_any(text, ("tokyo", "osaka", "kyoto", "city", "street")):
        matched = True
        _add_tags(tags, ("city", "travel", "street"))
        result.update(
            {
                "ai_description": "City travel or street photo",
                "scene_type": "city",
                "subject_type": "building",
                "suggested_use": "travel_memory",
                "ai_confidence": max(float(result["ai_confidence"]), 0.8),
            }
        )

    if _has_any(text, ("portrait", "selfie", "face", "people", "person")):
        matched = True
        _add_tags(tags, ("person", "portrait"))
        result.update(
            {
                "ai_description": "Portrait or person photo",
                "scene_type": "portrait",
                "subject_type": "person",
                "suggested_use": "social_media",
                "ai_confidence": max(float(result["ai_confidence"]), 0.8),
            }
        )

    if _has_any(text, ("plane", "airplane", "airport", "cockpit")):
        matched = True
        _add_tags(tags, ("airplane", "aviation", "travel"))
        result.update(
            {
                "ai_description": "Airplane or airport travel photo",
                "subject_type": "vehicle",
                "suggested_use": "documentary_b_roll",
                "ai_confidence": max(float(result["ai_confidence"]), 0.8),
            }
        )
        if result["scene_type"] == "unknown":
            result["scene_type"] = "travel"

    if _has_any(text, ("night", "dark")):
        matched = True
        _add_tags(tags, ("night",))
        result["scene_type"] = "night"
        if result["ai_description"] == "Unknown":
            result["ai_description"] = "Night or dark scene"
        result["ai_confidence"] = max(float(result["ai_confidence"]), 0.5)

    if matched:
        result["ai_tags"] = ", ".join(tags)

    if item.get("keep_recommendation") == "reject_candidate":
        result["suggested_use"] = "archive_only"
        if result["ai_confidence"]:
            result["ai_confidence"] = min(float(result["ai_confidence"]), 0.5)

    result["ai_confidence"] = round(float(result["ai_confidence"]), 2)
    return result


def _search_text(item: dict[str, Any]) -> str:
    values = [
        item.get("filename"),
        item.get("path"),
        item.get("camera_model"),
        item.get("lens_model"),
        item.get("thumbnail_path"),
    ]
    return " ".join(str(value).lower() for value in values if value not in (None, ""))


def _has_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(_has_keyword(text, keyword) for keyword in keywords)


def _has_keyword(text: str, keyword: str) -> bool:
    if keyword == "mt":
        return re.search(r"(^|[^a-z0-9])mt([^a-z0-9]|$)", text) is not None
    return keyword in text


def _add_tags(tags: list[str], new_tags: tuple[str, ...]) -> None:
    for tag in new_tags:
        if tag not in tags:
            tags.append(tag)

from __future__ import annotations

import csv
from pathlib import Path

from media_agent.export import export_csv
from media_agent.memory_safety import apply_memory_safe_recommendations
from media_agent.report import export_html_report


def test_memory_keyword_blurry_photo_is_review_not_reject() -> None:
    records = [
        _record(
            "friend_selfie_blurry.jpg",
            keep_recommendation="reject_candidate",
            recommendation_reason="blurry image",
            blur_score=25,
            exposure_score=90,
        )
    ]

    apply_memory_safe_recommendations(records)

    record = records[0]
    assert record["technical_recommendation"] == "reject_candidate"
    assert record["final_recommendation"] == "review"
    assert record["keep_recommendation"] == "review"
    assert record["memory_risk"] == "high"
    assert record["content_safety_override"] is True
    assert "memory-safe review recommended" in record["recommendation_reason"]


def test_low_memory_severe_blurry_photo_can_remain_reject_candidate() -> None:
    records = [
        _record(
            "ground_blurry.jpg",
            keep_recommendation="reject_candidate",
            recommendation_reason="blurry image",
            blur_score=20,
            exposure_score=90,
        )
    ]

    apply_memory_safe_recommendations(records)

    record = records[0]
    assert record["memory_risk"] == "low"
    assert record["final_recommendation"] == "reject_candidate"
    assert record["keep_recommendation"] == "reject_candidate"
    assert record["content_safety_override"] is False
    assert record["recommendation_reason"] == "technical reject candidate: severe blur"


def test_person_signal_reject_candidate_becomes_review() -> None:
    records = [
        _record(
            "technical_blurry_photo.jpg",
            keep_recommendation="reject_candidate",
            recommendation_reason="blurry image",
            blur_score=25,
            exposure_score=90,
            face_detected=True,
            face_count=1,
            person_signal=True,
            person_signal_confidence=0.7,
            person_signal_method="haar_face",
        )
    ]

    apply_memory_safe_recommendations(records)

    record = records[0]
    assert record["technical_recommendation"] == "reject_candidate"
    assert record["final_recommendation"] == "review"
    assert record["keep_recommendation"] == "review"
    assert record["memory_risk"] == "high"
    assert record["memory_risk_reason"] == "possible person or face detected"
    assert record["content_safety_override"] is True
    assert "possible person/face detected" in record["recommendation_reason"]


def test_duplicate_non_best_with_close_quality_becomes_review() -> None:
    records = [
        _record(
            "best_expression.jpg",
            keep_recommendation="keep",
            recommendation_reason="duplicate but best in group",
            blur_score=220,
            exposure_score=92,
            duplicate_group_id="dup_001",
            duplicate_count=2,
            group_best_pick=True,
            group_rank=1,
        ),
        _record(
            "alternate_expression.jpg",
            keep_recommendation="reject_candidate",
            recommendation_reason="duplicate and not best pick",
            blur_score=175,
            exposure_score=89,
            duplicate_group_id="dup_001",
            duplicate_count=2,
            group_best_pick=False,
            group_rank=2,
        ),
    ]

    apply_memory_safe_recommendations(records)

    alternate = records[1]
    assert alternate["technical_recommendation"] == "reject_candidate"
    assert alternate["final_recommendation"] == "review"
    assert alternate["keep_recommendation"] == "review"
    assert alternate["memory_risk"] == "medium"
    assert alternate["content_safety_override"] is True
    assert "different expression or moment" in alternate["recommendation_reason"]


def test_technically_good_unknown_content_keeps_with_content_not_evaluated_reason() -> None:
    records = [
        _record(
            "clean_unknown.jpg",
            keep_recommendation="keep",
            recommendation_reason="sharp image, good exposure",
            blur_score=420,
            exposure_score=94,
            ai_description="Unknown",
            ai_tags="",
        )
    ]

    apply_memory_safe_recommendations(records)

    record = records[0]
    assert record["final_recommendation"] == "keep"
    assert record["keep_recommendation"] == "keep"
    assert "content not evaluated" in record["recommendation_reason"]


def test_csv_and_html_include_memory_safe_fields(tmp_path: Path) -> None:
    records = [
        _record(
            "friend_selfie_blurry.jpg",
            keep_recommendation="reject_candidate",
            recommendation_reason="blurry image",
            blur_score=25,
            exposure_score=90,
        )
    ]
    apply_memory_safe_recommendations(records)

    csv_path = tmp_path / "media_index.csv"
    report_path = tmp_path / "report.html"
    export_csv(records, csv_path)
    export_html_report(records, report_path, language="en")

    csv_rows = list(csv.DictReader(csv_path.open(encoding="utf-8-sig")))
    assert csv_rows[0]["technical_recommendation"] == "reject_candidate"
    assert csv_rows[0]["final_recommendation"] == "review"
    assert csv_rows[0]["memory_risk"] == "high"
    assert csv_rows[0]["memory_risk_reason"] == "possible person or memory photo"
    assert csv_rows[0]["content_safety_override"] == "True"
    assert csv_rows[0]["face_detected"] == "False"
    assert csv_rows[0]["face_count"] == "0"
    assert csv_rows[0]["person_signal"] == "False"
    assert csv_rows[0]["person_signal_confidence"] == "0.0"
    assert csv_rows[0]["person_signal_method"] == "none"

    html = report_path.read_text(encoding="utf-8")
    assert "Technical Recommendation" in html
    assert "Final Recommendation" in html
    assert "Memory Risk" in html
    assert "Memory Risk Reason" in html
    assert "Content Safety Override" in html
    assert "memory-safe review" in html
    assert "Memory-Safe Override Count" in html
    assert "Face Detected" in html
    assert "Face Count" in html
    assert "Person Signal" in html
    assert "Person Signal Confidence" in html
    assert "Person Signal Method" in html
    assert "Face Detected Count" in html
    assert "Person Signal Count" in html
    assert "Person-Signal Memory-Safe Override Count" in html

    zh_report_path = tmp_path / "report_zh.html"
    export_html_report(records, zh_report_path, language="zh")
    zh_html = zh_report_path.read_text(encoding="utf-8")
    assert "技术建议" in zh_html
    assert "最终建议" in zh_html
    assert "回忆风险" in zh_html
    assert "回忆风险原因" in zh_html
    assert "内容保护覆盖" in zh_html
    assert "回忆保护复查" in zh_html
    assert "回忆保护覆盖数量" in zh_html
    assert "检测到人脸" in zh_html
    assert "人脸数量" in zh_html
    assert "人物信号" in zh_html
    assert "人物信号置信度" in zh_html
    assert "人物检测方法" in zh_html
    assert "检测到人脸数量" in zh_html
    assert "人物信号数量" in zh_html
    assert "人物保护覆盖数量" in zh_html


def _record(
    filename: str,
    *,
    keep_recommendation: str,
    recommendation_reason: str,
    blur_score: float,
    exposure_score: float,
    ai_description: str = "",
    ai_tags: str = "",
    duplicate_group_id: str = "",
    duplicate_count: int = 1,
    group_best_pick: bool | None = None,
    group_rank: int | None = None,
    face_detected: bool = False,
    face_count: int = 0,
    person_signal: bool = False,
    person_signal_confidence: float = 0.0,
    person_signal_method: str = "none",
) -> dict[str, object]:
    return {
        "filename": filename,
        "path": f"/tmp/{filename}",
        "width": 1920,
        "height": 1080,
        "file_size_bytes": 100,
        "created_at": "",
        "modified_at": "",
        "camera_model": "",
        "lens_model": "",
        "taken_at": "",
        "thumbnail_path": "",
        "face_detected": face_detected,
        "face_count": face_count,
        "person_signal": person_signal,
        "person_signal_confidence": person_signal_confidence,
        "person_signal_method": person_signal_method,
        "duplicate_group_id": duplicate_group_id,
        "duplicate_count": duplicate_count,
        "is_duplicate_candidate": bool(duplicate_group_id),
        "group_best_pick": group_best_pick,
        "group_rank": group_rank,
        "keep_recommendation": keep_recommendation,
        "recommendation_reason": recommendation_reason,
        "ai_description": ai_description,
        "ai_tags": ai_tags,
        "scene_type": "",
        "subject_type": "",
        "suggested_use": "",
        "ai_confidence": "",
        "ai_provider": "",
        "exposure_score": exposure_score,
        "overexposed_ratio": 0.0,
        "underexposed_ratio": 0.0,
        "blur_score": blur_score,
        "is_blurry": blur_score < 100,
        "waste_candidate": blur_score < 80,
        "quality_error": "",
    }

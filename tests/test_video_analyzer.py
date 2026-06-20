from __future__ import annotations

from pathlib import Path

from media_agent.video import analyzer


def test_video_analyzer_keeps_clear_well_exposed_keyframes(monkeypatch) -> None:
    def fake_quality(path: Path) -> dict[str, object]:
        return {
            "blur_score": 350.0,
            "exposure_score": 95.0,
            "overexposed_ratio": 0.0,
            "underexposed_ratio": 0.0,
            "is_blurry": False,
        }

    monkeypatch.setattr(analyzer, "analyze_quality", fake_quality)

    summary = analyzer.analyze_video_keyframes([Path("one.jpg"), Path("two.jpg")])

    assert summary["video_quality_recommendation"] == "keep"
    assert summary["frame_count"] == 2


def test_video_analyzer_rejects_majority_bad_keyframes(monkeypatch) -> None:
    results = iter(
        [
            {"blur_score": 30.0, "exposure_score": 90.0, "overexposed_ratio": 0.0, "underexposed_ratio": 0.0, "is_blurry": True},
            {"blur_score": 40.0, "exposure_score": 90.0, "overexposed_ratio": 0.0, "underexposed_ratio": 0.0, "is_blurry": True},
            {"blur_score": 350.0, "exposure_score": 95.0, "overexposed_ratio": 0.0, "underexposed_ratio": 0.0, "is_blurry": False},
        ]
    )

    monkeypatch.setattr(analyzer, "analyze_quality", lambda path: next(results))

    summary = analyzer.analyze_video_keyframes([Path("one.jpg"), Path("two.jpg"), Path("three.jpg")])

    assert summary["video_quality_recommendation"] == "reject_candidate"
    assert summary["blurry_frame_count"] == 2


def test_video_analyzer_reviews_shaky_clear_keyframes(monkeypatch) -> None:
    def fake_quality(path: Path) -> dict[str, object]:
        return {
            "blur_score": 350.0,
            "exposure_score": 95.0,
            "overexposed_ratio": 0.0,
            "underexposed_ratio": 0.0,
            "is_blurry": False,
        }

    monkeypatch.setattr(analyzer, "analyze_quality", fake_quality)
    monkeypatch.setattr(
        analyzer,
        "analyze_video_stability",
        lambda paths: {
            "stability_score": 45.0,
            "avg_motion": 16.0,
            "max_motion": 24.0,
            "shaky_frame_count": 1,
            "stability_recommendation": "shaky",
        },
    )

    summary = analyzer.analyze_video_keyframes([Path("one.jpg"), Path("two.jpg")])

    assert summary["video_quality_recommendation"] == "review"
    assert summary["recommendation_reason"] == "shaky keyframe motion, review needed"

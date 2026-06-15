from __future__ import annotations

from media_agent.best_pick import annotate_best_picks


def test_duplicate_group_has_only_one_best_pick() -> None:
    records = [
        _record("soft.jpg", blur_score=120, exposure_score=92, width=2000, height=1000),
        _record("sharp.jpg", blur_score=520, exposure_score=96, width=2000, height=1000),
        _record("dark.jpg", blur_score=300, exposure_score=35, width=4000, height=2000),
    ]

    annotate_best_picks(records)

    assert sum(1 for record in records if record["group_best_pick"] is True) == 1
    best = next(record for record in records if record["group_best_pick"] is True)
    assert best["filename"] == "sharp.jpg"
    assert best["group_rank"] == 1
    assert best["keep_recommendation"] == "keep"


def test_clear_and_well_exposed_image_ranks_higher() -> None:
    records = [
        _record("larger_but_soft.jpg", blur_score=180, exposure_score=92, width=6000, height=4000),
        _record("clear_balanced.jpg", blur_score=700, exposure_score=98, width=3000, height=2000),
    ]

    annotate_best_picks(records)

    ranked = sorted(records, key=lambda record: record["group_rank"])
    assert ranked[0]["filename"] == "clear_balanced.jpg"
    assert ranked[0]["recommendation_reason"] == "duplicate but best in group"
    assert ranked[1]["keep_recommendation"] == "reject_candidate"


def _record(
    filename: str,
    *,
    blur_score: float,
    exposure_score: float,
    width: int,
    height: int,
) -> dict[str, object]:
    return {
        "filename": filename,
        "duplicate_group_id": "dup_001",
        "blur_score": blur_score,
        "exposure_score": exposure_score,
        "overexposed_ratio": 0.0,
        "underexposed_ratio": 0.0,
        "waste_candidate": False,
        "width": width,
        "height": height,
    }

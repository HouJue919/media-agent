from __future__ import annotations

import csv
from pathlib import Path

from media_agent.video.organize import organize_videos_from_decisions


def test_video_copy_mode_does_not_delete_original_files(tmp_path: Path) -> None:
    source = tmp_path / "source.mp4"
    source.write_bytes(b"demo video")
    decisions = tmp_path / "video_decisions.csv"
    _write_video_decisions(decisions, [{"file_path": str(source), "user_decision": "keep"}])

    log_path = organize_videos_from_decisions(decisions, tmp_path / "organized_videos", mode="copy")

    assert source.exists()
    copied = tmp_path / "organized_videos" / "selected_video_keep" / "source.mp4"
    assert copied.exists()
    assert copied.read_bytes() == b"demo video"
    assert log_path == tmp_path / "organized_videos" / "video_organize_log.csv"


def test_duplicate_video_filenames_are_not_overwritten(tmp_path: Path) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    first_dir.mkdir()
    second_dir.mkdir()
    first = first_dir / "same.mp4"
    second = second_dir / "same.mp4"
    first.write_bytes(b"first")
    second.write_bytes(b"second")
    decisions = tmp_path / "video_decisions.csv"
    _write_video_decisions(
        decisions,
        [
            {"file_path": str(first), "user_decision": "review"},
            {"file_path": str(second), "user_decision": "review"},
        ],
    )

    organize_videos_from_decisions(decisions, tmp_path / "organized_videos", mode="copy")

    output_dir = tmp_path / "organized_videos" / "selected_video_review"
    outputs = sorted(path.name for path in output_dir.iterdir())
    assert outputs == ["same.mp4", "same_1.mp4"]
    assert {path.read_bytes() for path in output_dir.iterdir()} == {b"first", b"second"}


def test_video_organize_creates_all_decision_folders_and_log(tmp_path: Path) -> None:
    keep = tmp_path / "keep.mp4"
    review = tmp_path / "review.mov"
    reject = tmp_path / "reject.m4v"
    keep.write_bytes(b"keep")
    review.write_bytes(b"review")
    reject.write_bytes(b"reject")
    decisions = tmp_path / "video_decisions.csv"
    _write_video_decisions(
        decisions,
        [
            {"file_path": str(keep), "user_decision": "keep"},
            {"file_path": str(review), "user_decision": "review"},
            {"file_path": str(reject), "user_decision": "reject"},
        ],
    )

    output_dir = tmp_path / "organized_videos"
    log_path = organize_videos_from_decisions(decisions, output_dir, mode="copy")

    assert (output_dir / "selected_video_keep" / "keep.mp4").exists()
    assert (output_dir / "selected_video_review" / "review.mov").exists()
    assert (output_dir / "selected_video_reject" / "reject.m4v").exists()
    log_rows = list(csv.DictReader(log_path.open(encoding="utf-8-sig")))
    assert len(log_rows) == 3
    assert {row["status"] for row in log_rows} == {"success"}
    assert {row["action"] for row in log_rows} == {"copy"}


def _write_video_decisions(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["file_path", "video_quality_recommendation", "user_decision"],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({"video_quality_recommendation": "", **row})

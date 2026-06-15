from __future__ import annotations

import csv
from pathlib import Path

from media_agent.organize import organize_from_decisions


def test_copy_mode_does_not_delete_original_files(tmp_path: Path) -> None:
    source = tmp_path / "source.jpg"
    source.write_bytes(b"demo image")
    decisions = tmp_path / "decisions.csv"
    _write_decisions(decisions, [{"file_path": str(source), "user_decision": "keep"}])

    organize_from_decisions(decisions, tmp_path / "organized", mode="copy")

    assert source.exists()
    copied = tmp_path / "organized" / "selected_keep" / "source.jpg"
    assert copied.exists()
    assert copied.read_bytes() == b"demo image"


def test_duplicate_filenames_are_not_overwritten(tmp_path: Path) -> None:
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    first_dir.mkdir()
    second_dir.mkdir()
    first = first_dir / "same.jpg"
    second = second_dir / "same.jpg"
    first.write_bytes(b"first")
    second.write_bytes(b"second")
    decisions = tmp_path / "decisions.csv"
    _write_decisions(
        decisions,
        [
            {"file_path": str(first), "user_decision": "review"},
            {"file_path": str(second), "user_decision": "review"},
        ],
    )

    organize_from_decisions(decisions, tmp_path / "organized", mode="copy")

    output_dir = tmp_path / "organized" / "selected_review"
    outputs = sorted(path.name for path in output_dir.iterdir())
    assert outputs == ["same.jpg", "same_1.jpg"]
    assert {path.read_bytes() for path in output_dir.iterdir()} == {b"first", b"second"}


def _write_decisions(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["file_path", "keep_recommendation", "user_decision"])
        writer.writeheader()
        for row in rows:
            writer.writerow({"keep_recommendation": "", **row})

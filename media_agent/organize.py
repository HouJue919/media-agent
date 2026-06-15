from __future__ import annotations

import csv
import shutil
from pathlib import Path
from typing import Any


DECISION_TO_FOLDER = {
    "keep": "selected_keep",
    "review": "selected_review",
    "reject": "selected_reject",
}

LOG_FIELDS = [
    "original_path",
    "target_path",
    "user_decision",
    "action",
    "status",
]


def organize_from_decisions(decisions_path: Path, output_dir: Path, mode: str = "copy") -> Path:
    if mode not in {"copy", "move"}:
        raise ValueError("mode must be 'copy' or 'move'")
    if not decisions_path.exists():
        raise FileNotFoundError(f"Decisions file does not exist: {decisions_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    for folder_name in DECISION_TO_FOLDER.values():
        (output_dir / folder_name).mkdir(parents=True, exist_ok=True)

    log_records = []
    for row in _read_decisions(decisions_path):
        log_records.append(_organize_row(row, output_dir, mode))

    log_path = output_dir / "organize_log.csv"
    _write_log(log_records, log_path)
    return log_path


def _read_decisions(decisions_path: Path) -> list[dict[str, Any]]:
    with decisions_path.open("r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def _organize_row(row: dict[str, Any], output_dir: Path, mode: str) -> dict[str, str]:
    original_path_text = str(row.get("file_path") or "").strip()
    user_decision = str(row.get("user_decision") or "").strip().lower()
    log_record = {
        "original_path": original_path_text,
        "target_path": "",
        "user_decision": user_decision,
        "action": "skip",
        "status": "pending",
    }

    if not original_path_text:
        log_record["status"] = "skipped_missing_file_path"
        return log_record
    if not user_decision:
        log_record["status"] = "skipped_no_user_decision"
        return log_record
    if user_decision not in DECISION_TO_FOLDER:
        log_record["status"] = "skipped_invalid_user_decision"
        return log_record

    source_path = Path(original_path_text).expanduser()
    if not source_path.exists():
        log_record["status"] = "error_source_not_found"
        return log_record
    if not source_path.is_file():
        log_record["status"] = "error_source_not_file"
        return log_record

    target_dir = output_dir / DECISION_TO_FOLDER[user_decision]
    target_path = _unique_target_path(target_dir / source_path.name)
    log_record["target_path"] = str(target_path)
    log_record["action"] = mode

    try:
        if mode == "copy":
            shutil.copy2(source_path, target_path)
        else:
            shutil.move(str(source_path), str(target_path))
    except Exception as exc:
        log_record["status"] = f"error_{type(exc).__name__}: {exc}"
        return log_record

    log_record["status"] = "success"
    return log_record


def _unique_target_path(target_path: Path) -> Path:
    if not target_path.exists():
        return target_path

    stem = target_path.stem
    suffix = target_path.suffix
    parent = target_path.parent
    counter = 1

    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def _write_log(records: list[dict[str, str]], log_path: Path) -> None:
    with log_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=LOG_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

from __future__ import annotations

import argparse
from pathlib import Path

from media_agent.organize import organize_from_decisions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan photo media files, export reports, or organize files from decisions.csv."
    )
    parser.add_argument("folder", nargs="?", help="Folder to scan for image files.")
    parser.add_argument(
        "-o",
        "--output",
        default="media_index.csv",
        help="Output CSV path. Defaults to media_index.csv.",
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Only scan files directly inside the folder.",
    )
    parser.add_argument(
        "--thumbnail-dir",
        default=None,
        help="Directory for generated thumbnails. Defaults to thumbnails next to the CSV.",
    )
    parser.add_argument(
        "--report",
        default="report.html",
        help="Output HTML report path. Defaults to report.html.",
    )
    parser.add_argument(
        "--language",
        choices=("zh", "en"),
        default="zh",
        help="HTML report language: zh or en. Defaults to zh.",
    )
    parser.add_argument(
        "--enable-ai-tags",
        action="store_true",
        help="Enable mock/local AI tagging fields in CSV and HTML report.",
    )
    parser.add_argument(
        "--ai-provider",
        default="mock",
        help="AI tagging provider. Only mock is supported in v2.0.",
    )
    parser.add_argument(
        "--decisions",
        default=None,
        help="Read decisions.csv and organize files instead of scanning a folder.",
    )
    parser.add_argument(
        "--organize-output",
        default="organized_media",
        help="Output directory for organized files. Defaults to organized_media.",
    )
    parser.add_argument(
        "--mode",
        choices=("copy", "move"),
        default="copy",
        help="Organize mode: copy or move. Defaults to copy.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.ai_provider != "mock":
        raise SystemExit("Only mock provider is supported in v2.0.")

    if args.decisions:
        decisions_path = Path(args.decisions).expanduser().resolve()
        organize_output = Path(args.organize_output).expanduser().resolve()
        log_path = organize_from_decisions(decisions_path, organize_output, mode=args.mode)
        print(f"Decisions read from: {decisions_path}")
        print(f"Organized media written to: {organize_output}")
        print(f"Organize log written to: {log_path}")
        return

    if not args.folder:
        raise SystemExit("Folder is required unless --decisions is provided.")

    from media_agent.best_pick import annotate_best_picks
    from media_agent.ai_tagging.tagger import EMPTY_AI_TAGS, tag_media_item
    from media_agent.export import export_csv
    from media_agent.metadata import build_media_record
    from media_agent.quality import analyze_quality
    from media_agent.report import export_html_report, sort_records_for_review
    from media_agent.scanner import scan_media_files
    from media_agent.similarity import annotate_duplicate_groups
    from media_agent.thumbnail import create_thumbnail

    folder = Path(args.folder).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    thumbnail_dir = (
        Path(args.thumbnail_dir).expanduser().resolve()
        if args.thumbnail_dir
        else output.parent / "thumbnails"
    )
    report_path = Path(args.report).expanduser().resolve()

    if not folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder}")
    if not folder.is_dir():
        raise NotADirectoryError(f"Path is not a folder: {folder}")

    files = scan_media_files(folder, recursive=not args.no_recursive)
    records = []

    for file_path in files:
        record = build_media_record(file_path)
        quality = analyze_quality(file_path)
        thumbnail_path = create_thumbnail(file_path, thumbnail_dir)
        record.update(quality)
        record["thumbnail_path"] = str(thumbnail_path) if thumbnail_path else None
        records.append(record)

    annotate_duplicate_groups(records)
    annotate_best_picks(records)
    for record in records:
        record.update(tag_media_item(record) if args.enable_ai_tags else EMPTY_AI_TAGS)
    records = sort_records_for_review(records)
    export_csv(records, output)
    export_html_report(records, report_path, language=args.language)
    print(f"Scanned {len(records)} media files.")
    print(f"CSV written to: {output}")
    print(f"Thumbnails written to: {thumbnail_dir}")
    print(f"HTML report written to: {report_path}")


if __name__ == "__main__":
    main()

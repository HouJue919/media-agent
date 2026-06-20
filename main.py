from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from media_agent.organize import organize_from_decisions


DEFAULT_PHOTO_OUTPUT = "media_index.csv"
DEFAULT_VIDEO_OUTPUT = "video_index.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan photo/video media files, export reports, or organize files from decisions.csv."
    )
    parser.add_argument("folder", nargs="?", help="Folder to scan for media files.")
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_PHOTO_OUTPUT,
        help="Output CSV path. Defaults to media_index.csv for photo mode and video_index.csv for video mode.",
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
        help="AI tagging provider. Only mock is supported.",
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
        "--video-decisions",
        default=None,
        help="Read video_decisions.csv and organize videos when --mode video-organize is used.",
    )
    parser.add_argument(
        "--video-organize-output",
        default="organized_videos",
        help="Output directory for organized videos. Defaults to organized_videos.",
    )
    parser.add_argument(
        "--mode-action",
        choices=("copy", "move"),
        default="copy",
        help="Video organize action: copy or move. Defaults to copy.",
    )
    parser.add_argument(
        "--mode",
        default="photo",
        help="Mode: photo, video, or video-organize. Legacy copy/move values are accepted with --decisions.",
    )
    parser.add_argument(
        "--organize-mode",
        choices=("copy", "move"),
        default=None,
        help="Organize mode for --decisions: copy or move. Defaults to copy.",
    )
    parser.add_argument(
        "--frame-interval",
        type=float,
        default=5.0,
        help="Video mode only: extract one keyframe every N seconds. Defaults to 5.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=12,
        help="Video mode only: maximum keyframes to extract per video. Defaults to 12.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.ai_provider != "mock":
        raise SystemExit("Only mock provider is supported.")

    if args.mode == "video-organize":
        _run_video_organize_workflow(args)
        return

    if args.decisions:
        decisions_path = Path(args.decisions).expanduser().resolve()
        organize_output = Path(args.organize_output).expanduser().resolve()
        organize_mode = _resolve_organize_mode(args)
        log_path = organize_from_decisions(decisions_path, organize_output, mode=organize_mode)
        print(f"Decisions read from: {decisions_path}")
        print(f"Organized media written to: {organize_output}")
        print(f"Organize log written to: {log_path}")
        return

    if not args.folder:
        raise SystemExit("Folder is required unless --decisions is provided.")

    folder = Path(args.folder).expanduser().resolve()
    if not folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder}")
    if not folder.is_dir():
        raise NotADirectoryError(f"Path is not a folder: {folder}")

    if args.mode == "photo":
        _run_photo_workflow(args, folder)
        return
    if args.mode == "video":
        _run_video_workflow(args, folder)
        return
    raise SystemExit(
        "Mode must be 'photo', 'video', or 'video-organize'. "
        "Use --organize-mode copy|move with --decisions for photo organization."
    )


def _resolve_organize_mode(args: argparse.Namespace) -> str:
    if args.organize_mode:
        return args.organize_mode
    if args.mode in {"copy", "move"}:
        return args.mode
    return "copy"


def _run_photo_workflow(args: argparse.Namespace, folder: Path) -> None:
    from media_agent.ai_tagging.tagger import EMPTY_AI_TAGS, tag_media_item
    from media_agent.best_pick import annotate_best_picks
    from media_agent.export import export_csv
    from media_agent.metadata import build_media_record
    from media_agent.quality import analyze_quality
    from media_agent.report import export_html_report, sort_records_for_review
    from media_agent.scanner import scan_media_files
    from media_agent.similarity import annotate_duplicate_groups
    from media_agent.thumbnail import create_thumbnail

    output = Path(args.output).expanduser().resolve()
    thumbnail_dir = (
        Path(args.thumbnail_dir).expanduser().resolve()
        if args.thumbnail_dir
        else output.parent / "thumbnails"
    )
    report_path = Path(args.report).expanduser().resolve()
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


def _run_video_organize_workflow(args: argparse.Namespace) -> None:
    from media_agent.video.organize import organize_videos_from_decisions

    if not args.video_decisions:
        raise SystemExit("--video-decisions is required when --mode video-organize is used.")

    decisions_path = Path(args.video_decisions).expanduser().resolve()
    organize_output = Path(args.video_organize_output).expanduser().resolve()
    log_path = organize_videos_from_decisions(decisions_path, organize_output, mode=args.mode_action)
    print(f"Video decisions read from: {decisions_path}")
    print(f"Organized videos written to: {organize_output}")
    print(f"Video organize log written to: {log_path}")


def _run_video_workflow(args: argparse.Namespace, folder: Path) -> None:
    from media_agent.video.analyzer import analyze_video_keyframes
    from media_agent.video.export import export_video_csv
    from media_agent.video.keyframes import extract_keyframes
    from media_agent.video.metadata import read_video_metadata
    from media_agent.video.report import export_video_html_report, sort_video_records
    from media_agent.video.scanner import scan_video_files

    if args.frame_interval <= 0:
        raise SystemExit("--frame-interval must be greater than 0.")
    if args.max_frames <= 0:
        raise SystemExit("--max-frames must be greater than 0.")

    output_name = DEFAULT_VIDEO_OUTPUT if args.output == DEFAULT_PHOTO_OUTPUT else args.output
    output = Path(output_name).expanduser().resolve()
    report_path = Path(args.report).expanduser().resolve()
    keyframe_root = report_path.parent / "video_keyframes"

    files = scan_video_files(folder, recursive=not args.no_recursive)
    records: list[dict[str, Any]] = []

    for file_path in files:
        record = read_video_metadata(file_path)
        keyframe_paths = extract_keyframes(file_path, keyframe_root, args.frame_interval, args.max_frames)
        keyframe_dir = keyframe_root / file_path.stem
        record["keyframe_dir"] = str(keyframe_dir)
        record["keyframe_paths"] = [str(path) for path in keyframe_paths]
        record.update(analyze_video_keyframes(keyframe_paths))
        records.append(record)

    records = sort_video_records(records)
    export_video_csv(records, output)
    export_video_html_report(records, report_path, language=args.language)
    print(f"Scanned {len(records)} video files.")
    print(f"CSV written to: {output}")
    print(f"Keyframes written to: {keyframe_root}")
    print(f"HTML report written to: {report_path}")


if __name__ == "__main__":
    main()

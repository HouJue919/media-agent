from __future__ import annotations

import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent


def build_photo_command(
    folder_path: str,
    *,
    language: str = "zh",
    report: str = "report_zh.html",
    output: str = "media_index.csv",
    enable_ai_tags: bool = False,
    python_executable: str | None = None,
) -> list[str]:
    command = [
        python_executable or sys.executable,
        str(PROJECT_ROOT / "main.py"),
        folder_path,
        "--mode",
        "photo",
        "--language",
        language,
        "--report",
        report,
        "--output",
        output,
    ]
    if enable_ai_tags:
        command.extend(["--enable-ai-tags", "--ai-provider", "mock"])
    return command


def build_video_command(
    folder_path: str,
    *,
    language: str = "zh",
    report: str = "video_report_zh.html",
    output: str = "video_index.csv",
    frame_interval: float = 5,
    max_frames: int = 12,
    python_executable: str | None = None,
) -> list[str]:
    return [
        python_executable or sys.executable,
        str(PROJECT_ROOT / "main.py"),
        folder_path,
        "--mode",
        "video",
        "--language",
        language,
        "--report",
        report,
        "--output",
        output,
        "--frame-interval",
        str(frame_interval),
        "--max-frames",
        str(max_frames),
    ]


def build_photo_organize_command(
    decisions_path: str,
    *,
    organize_output: str = "organized_media",
    organize_mode: str = "copy",
    python_executable: str | None = None,
) -> list[str]:
    return [
        python_executable or sys.executable,
        str(PROJECT_ROOT / "main.py"),
        "--decisions",
        decisions_path,
        "--organize-output",
        organize_output,
        "--organize-mode",
        organize_mode,
    ]


def build_video_organize_command(
    decisions_path: str,
    *,
    organize_output: str = "organized_videos",
    organize_mode: str = "copy",
    python_executable: str | None = None,
) -> list[str]:
    return [
        python_executable or sys.executable,
        str(PROJECT_ROOT / "main.py"),
        "--mode",
        "video-organize",
        "--video-decisions",
        decisions_path,
        "--video-organize-output",
        organize_output,
        "--mode-action",
        organize_mode,
    ]


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def parse_cli_output(stdout: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if line.startswith("Scanned "):
            result["scanned"] = line
        elif line.startswith("CSV written to:"):
            result["csv_path"] = line.split(":", 1)[1].strip()
        elif line.startswith("HTML report written to:"):
            result["report_path"] = line.split(":", 1)[1].strip()
        elif line.startswith("Thumbnails written to:"):
            result["thumbnails_path"] = line.split(":", 1)[1].strip()
        elif line.startswith("Keyframes written to:"):
            result["keyframes_path"] = line.split(":", 1)[1].strip()
        elif line.startswith("Organized media written to:"):
            result["organized_path"] = line.split(":", 1)[1].strip()
        elif line.startswith("Organized videos written to:"):
            result["organized_path"] = line.split(":", 1)[1].strip()
        elif line.startswith("Organize log written to:"):
            result["log_path"] = line.split(":", 1)[1].strip()
        elif line.startswith("Video organize log written to:"):
            result["log_path"] = line.split(":", 1)[1].strip()
    return result


def resolve_report_path(report: str) -> Path:
    path = Path(report).expanduser()
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def main() -> None:
    try:
        import streamlit as st
    except ImportError as exc:
        raise SystemExit(
            "Streamlit is not installed. Install GUI dependencies with: "
            "pip install -r requirements-gui.txt"
        ) from exc

    st.set_page_config(page_title="Media Agent", layout="wide")
    st.title("Media Agent")
    st.caption("AI-assisted photo and video asset management for creators.")

    mode = st.selectbox(
        "Mode",
        ["Photo Analysis", "Video Analysis", "Organize Photos", "Organize Videos"],
    )

    command: list[str] | None = None
    report_path_for_open: Path | None = None

    if mode in {"Photo Analysis", "Video Analysis"}:
        folder_path = st.text_input(
            "Photo/Video Folder Path",
            placeholder="/path/to/photos-or-videos",
        )
        language = st.selectbox("Language", ["zh", "en"], index=0)
        open_report = st.checkbox("Open report after generation", value=True)

        if mode == "Photo Analysis":
            enable_ai_tags = st.checkbox("Enable mock AI tags", value=False)
            st.text_input("AI Provider", value="mock", disabled=True)
            report = st.text_input("Report filename", value=f"report_{language}.html")
            output = st.text_input("CSV filename", value="media_index.csv")
            command = build_photo_command(
                folder_path,
                language=language,
                report=report,
                output=output,
                enable_ai_tags=enable_ai_tags,
            )
        else:
            frame_interval = st.number_input("Frame interval seconds", min_value=0.5, value=5.0, step=0.5)
            max_frames = st.number_input("Max frames per video", min_value=1, value=12, step=1)
            report = st.text_input("Report filename", value=f"video_report_{language}.html")
            output = st.text_input("CSV filename", value="video_index.csv")
            command = build_video_command(
                folder_path,
                language=language,
                report=report,
                output=output,
                frame_interval=float(frame_interval),
                max_frames=int(max_frames),
            )
        report_path_for_open = resolve_report_path(report)
        _render_run_button(st, command, report_path_for_open, open_report, required_path=folder_path)

    elif mode == "Organize Photos":
        decisions_path = st.text_input("decisions.csv path", value="decisions.csv")
        organize_output = st.text_input("Organize output folder", value="organized_media")
        organize_mode = st.selectbox("Mode action", ["copy", "move"], index=0)
        command = build_photo_organize_command(
            decisions_path,
            organize_output=organize_output,
            organize_mode=organize_mode,
        )
        _render_run_button(st, command, None, False, required_path=decisions_path)

    else:
        decisions_path = st.text_input("video_decisions.csv path", value="video_decisions.csv")
        organize_output = st.text_input("Organize output folder", value="organized_videos")
        organize_mode = st.selectbox("Mode action", ["copy", "move"], index=0)
        command = build_video_organize_command(
            decisions_path,
            organize_output=organize_output,
            organize_mode=organize_mode,
        )
        _render_run_button(st, command, None, False, required_path=decisions_path)


def _render_run_button(
    st: Any,
    command: list[str],
    report_path_for_open: Path | None,
    open_report: bool,
    *,
    required_path: str,
) -> None:
    st.code(" ".join(command), language="bash")
    if not st.button("Run"):
        return

    if not required_path.strip():
        st.error("Please enter a folder or file path.")
        return

    with st.spinner("Running Media Agent..."):
        completed = run_command(command)

    if completed.returncode == 0:
        st.success("Media Agent completed successfully.")
        result = parse_cli_output(completed.stdout)
        _render_result_summary(st, result)
        if completed.stdout:
            with st.expander("Command output"):
                st.code(completed.stdout)
        if report_path_for_open and open_report:
            webbrowser.open(report_path_for_open.as_uri())
            st.info(f"Report opened locally: {report_path_for_open}")
    else:
        st.error("Media Agent failed.")
        if completed.stdout:
            with st.expander("Command output"):
                st.code(completed.stdout)
        if completed.stderr:
            with st.expander("Error output", expanded=True):
                st.code(completed.stderr)


def _render_result_summary(st: Any, result: dict[str, str]) -> None:
    if not result:
        return
    labels = {
        "scanned": "Scanned count",
        "csv_path": "Output CSV path",
        "report_path": "Report path",
        "thumbnails_path": "Thumbnails path",
        "keyframes_path": "Keyframes path",
        "organized_path": "Organized output path",
        "log_path": "Log path",
    }
    for key, label in labels.items():
        if key in result:
            st.write(f"**{label}:** `{result[key]}`")


if __name__ == "__main__":
    main()

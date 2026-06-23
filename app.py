from __future__ import annotations

import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent
APP_TITLE = "Media Agent"
APP_SUBTITLE = "Local photo and video asset management for creators."
PRIVACY_NOTICE = "All processing runs locally. Media files are not uploaded."
GITHUB_REPO_URL = "https://github.com/HouJue919/media-agent"


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

    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)
    st.info(PRIVACY_NOTICE)

    analyze_tab, organize_tab, help_tab = st.tabs(["Analyze", "Organize", "Help"])
    with analyze_tab:
        _render_analyze_tab(st)
    with organize_tab:
        _render_organize_tab(st)
    with help_tab:
        _render_help_tab(st)


def _render_analyze_tab(st: Any) -> None:
    analysis_mode = st.radio(
        "Analysis Type",
        ["Photo Analysis", "Video Analysis"],
        horizontal=True,
    )
    folder_path = st.text_input(
        "Photo/Video Folder Path",
        placeholder="/path/to/photos-or-videos",
    )
    language = st.selectbox("Language", ["zh", "en"], index=0)
    open_report = st.checkbox("Open report after generation", value=True)

    if analysis_mode == "Photo Analysis":
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
        left, right = st.columns(2)
        with left:
            frame_interval = st.number_input("Frame interval seconds", min_value=0.5, value=5.0, step=0.5)
        with right:
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

    _render_run_button(
        st,
        command,
        resolve_report_path(report),
        open_report,
        required_path=folder_path,
        button_label="Run Analysis",
    )


def _render_organize_tab(st: Any) -> None:
    organize_mode = st.radio(
        "Organize Type",
        ["Organize Photos", "Organize Videos"],
        horizontal=True,
    )
    st.warning("copy is recommended; move changes file locations")
    action = st.selectbox("Mode action", ["copy", "move"], index=0)

    if organize_mode == "Organize Photos":
        decisions_path = st.text_input("Decisions file path", value="decisions.csv")
        organize_output = st.text_input("Output folder", value="organized_media")
        command = build_photo_organize_command(
            decisions_path,
            organize_output=organize_output,
            organize_mode=action,
        )
    else:
        decisions_path = st.text_input("Decisions file path", value="video_decisions.csv")
        organize_output = st.text_input("Output folder", value="organized_videos")
        command = build_video_organize_command(
            decisions_path,
            organize_output=organize_output,
            organize_mode=action,
        )

    _render_run_button(
        st,
        command,
        None,
        False,
        required_path=decisions_path,
        button_label="Run Organization",
    )


def _render_help_tab(st: Any) -> None:
    st.subheader("Basic workflow")
    st.markdown(
        """
- Photo: scan -> review -> export decisions -> organize
- Video: scan -> keyframes -> review -> export decisions -> organize
        """.strip()
    )

    st.subheader("CLI fallback examples")
    st.code(
        "\n".join(
            [
                "python main.py /path/to/photos --language en --report report_en.html --enable-ai-tags --ai-provider mock",
                "python main.py /path/to/videos --mode video --language en --report video_report.html --frame-interval 5 --max-frames 12",
                "python main.py --decisions decisions.csv --organize-output organized_media --organize-mode copy",
                "python main.py --mode video-organize --video-decisions video_decisions.csv --video-organize-output organized_videos --mode-action copy",
            ]
        ),
        language="bash",
    )
    st.markdown(f"GitHub repo: [{GITHUB_REPO_URL}]({GITHUB_REPO_URL})")


def _render_run_button(
    st: Any,
    command: list[str],
    report_path_for_open: Path | None,
    open_report: bool,
    *,
    required_path: str,
    button_label: str,
) -> None:
    st.subheader("Final command")
    st.code(" ".join(command), language="bash")
    if not st.button(button_label):
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
        _render_result_links(st, result)
        if completed.stdout:
            with st.expander("stdout"):
                st.code(completed.stdout)
        if report_path_for_open and open_report:
            webbrowser.open(report_path_for_open.as_uri())
            st.info(f"Report opened locally: {report_path_for_open}")
    else:
        st.error("Media Agent failed.")
        if completed.stdout:
            with st.expander("stdout"):
                st.code(completed.stdout)
        if completed.stderr:
            with st.expander("stderr", expanded=True):
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


def _render_result_links(st: Any, result: dict[str, str]) -> None:
    link_targets = [
        ("Open report", result.get("report_path")),
        ("Open CSV", result.get("csv_path")),
        ("Open thumbnails folder", result.get("thumbnails_path")),
        ("Open keyframes folder", result.get("keyframes_path")),
        ("Open organized folder", result.get("organized_path")),
    ]
    for label, raw_path in link_targets:
        if not raw_path:
            continue
        path = Path(raw_path).expanduser()
        if not path.exists():
            continue
        if hasattr(st, "link_button"):
            st.link_button(label, path.resolve().as_uri())
        else:
            st.write(f"{label}: {path.resolve().as_uri()}")


if __name__ == "__main__":
    main()

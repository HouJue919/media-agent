from __future__ import annotations

import subprocess
import sys
import webbrowser
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent
GITHUB_REPO_URL = "https://github.com/HouJue919/media-agent"

UI_TEXT = {
    "en": {
        "app_title": "Media Agent",
        "subtitle": "Local photo and video asset management for creators.",
        "privacy": "All processing runs locally. Media files are not uploaded.",
        "interface_language": "Interface Language",
        "tab_analyze": "Analyze",
        "tab_organize": "Organize",
        "tab_help": "Help",
        "mode": "Mode",
        "photo_analysis": "Photo Analysis",
        "video_analysis": "Video Analysis",
        "organize_photos": "Organize Photos",
        "organize_videos": "Organize Videos",
        "folder_path": "Photo/Video Folder Path",
        "report_language": "Report Language",
        "open_report": "Open report after generation",
        "enable_ai_tags": "Enable Mock AI Tags",
        "ai_provider": "AI Provider",
        "frame_interval": "Frame Interval",
        "max_frames": "Max Frames",
        "report_filename": "Report Filename",
        "csv_filename": "CSV Filename",
        "decisions_path": "Decisions CSV Path",
        "output_folder": "Output Folder",
        "mode_action": "Mode / Action",
        "copy": "copy",
        "move": "move",
        "copy_recommended": "Copy is recommended; move changes file locations.",
        "run_analysis": "Run Analysis",
        "run_organize": "Run Organize",
        "final_command": "Final command",
        "success": "Media Agent completed successfully.",
        "failed": "Media Agent failed.",
        "missing_path": "Please enter a folder or file path.",
        "scanned": "Scanned count",
        "csv_path": "CSV path",
        "report_path": "Report path",
        "thumbnails_path": "Thumbnails path",
        "keyframes_path": "Keyframes path",
        "organized_path": "Organized output path",
        "log_path": "Log path",
        "open_report_link": "Open report",
        "open_csv_link": "Open CSV",
        "open_thumbnails_link": "Open thumbnails folder",
        "open_keyframes_link": "Open keyframes folder",
        "open_organized_link": "Open organized folder",
        "report_opened": "Report opened locally:",
        "show_stdout": "Show stdout",
        "show_stderr": "Show stderr",
        "basic_workflow": "Basic Workflow",
        "photo_workflow": "Photo: scan -> review -> export decisions -> organize",
        "video_workflow": "Video: scan -> keyframes -> review -> export decisions -> organize",
        "cli_examples": "CLI fallback examples",
        "github_repo": "GitHub repo",
    },
    "zh": {
        "app_title": "Media Agent",
        "subtitle": "面向创作者的本地照片与视频素材管理工具。",
        "privacy": "所有处理都在本地运行，媒体文件不会被上传。",
        "interface_language": "界面语言",
        "tab_analyze": "分析",
        "tab_organize": "整理",
        "tab_help": "帮助",
        "mode": "模式",
        "photo_analysis": "照片分析",
        "video_analysis": "视频分析",
        "organize_photos": "整理照片",
        "organize_videos": "整理视频",
        "folder_path": "照片/视频文件夹路径",
        "report_language": "报告语言",
        "open_report": "生成后打开报告",
        "enable_ai_tags": "启用 Mock AI 标签",
        "ai_provider": "AI 来源",
        "frame_interval": "抽帧间隔",
        "max_frames": "最大关键帧数",
        "report_filename": "报告文件名",
        "csv_filename": "CSV 文件名",
        "decisions_path": "决策 CSV 路径",
        "output_folder": "输出文件夹",
        "mode_action": "模式/操作",
        "copy": "复制",
        "move": "移动",
        "copy_recommended": "建议使用复制；移动会改变文件位置。",
        "run_analysis": "运行分析",
        "run_organize": "运行整理",
        "final_command": "最终命令",
        "success": "Media Agent 已成功完成。",
        "failed": "Media Agent 运行失败。",
        "missing_path": "请输入文件夹或文件路径。",
        "scanned": "扫描数量",
        "csv_path": "CSV 路径",
        "report_path": "报告路径",
        "thumbnails_path": "缩略图路径",
        "keyframes_path": "关键帧路径",
        "organized_path": "整理输出路径",
        "log_path": "日志路径",
        "open_report_link": "打开报告",
        "open_csv_link": "打开 CSV",
        "open_thumbnails_link": "打开缩略图文件夹",
        "open_keyframes_link": "打开关键帧文件夹",
        "open_organized_link": "打开整理输出文件夹",
        "report_opened": "已在本地打开报告：",
        "show_stdout": "查看 stdout",
        "show_stderr": "查看 stderr",
        "basic_workflow": "基本工作流",
        "photo_workflow": "照片：扫描 -> 复查 -> 导出决策 -> 整理",
        "video_workflow": "视频：扫描 -> 抽帧 -> 复查 -> 导出决策 -> 整理",
        "cli_examples": "CLI 备用示例",
        "github_repo": "GitHub 仓库",
    },
}

APP_TITLE = UI_TEXT["en"]["app_title"]
APP_SUBTITLE = UI_TEXT["en"]["subtitle"]
PRIVACY_NOTICE = UI_TEXT["en"]["privacy"]


def t(key: str, language: str = "en") -> str:
    return UI_TEXT.get(language, UI_TEXT["en"]).get(key, key)


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
    interface_choice = st.selectbox("Interface Language / 界面语言", ["English", "中文"], index=0)
    interface_language = "zh" if interface_choice == "中文" else "en"
    st.title(t("app_title", interface_language))
    st.caption(t("subtitle", interface_language))
    st.info(t("privacy", interface_language))

    analyze_tab, organize_tab, help_tab = st.tabs(
        [
            t("tab_analyze", interface_language),
            t("tab_organize", interface_language),
            t("tab_help", interface_language),
        ]
    )
    with analyze_tab:
        _render_analyze_tab(st, interface_language)
    with organize_tab:
        _render_organize_tab(st, interface_language)
    with help_tab:
        _render_help_tab(st, interface_language)


def _render_analyze_tab(st: Any, interface_language: str) -> None:
    analysis_options = {
        t("photo_analysis", interface_language): "photo",
        t("video_analysis", interface_language): "video",
    }
    analysis_mode = st.radio(
        t("mode", interface_language),
        list(analysis_options.keys()),
        horizontal=True,
    )
    folder_path = st.text_input(
        t("folder_path", interface_language),
        placeholder="/path/to/photos-or-videos",
    )
    report_language = st.selectbox(t("report_language", interface_language), ["zh", "en"], index=0)
    open_report = st.checkbox(t("open_report", interface_language), value=True)

    if analysis_options[analysis_mode] == "photo":
        enable_ai_tags = st.checkbox(t("enable_ai_tags", interface_language), value=False)
        st.text_input(t("ai_provider", interface_language), value="mock", disabled=True)
        report = st.text_input(t("report_filename", interface_language), value=f"report_{report_language}.html")
        output = st.text_input(t("csv_filename", interface_language), value="media_index.csv")
        command = build_photo_command(
            folder_path,
            language=report_language,
            report=report,
            output=output,
            enable_ai_tags=enable_ai_tags,
        )
    else:
        left, right = st.columns(2)
        with left:
            frame_interval = st.number_input(t("frame_interval", interface_language), min_value=0.5, value=5.0, step=0.5)
        with right:
            max_frames = st.number_input(t("max_frames", interface_language), min_value=1, value=12, step=1)
        report = st.text_input(t("report_filename", interface_language), value=f"video_report_{report_language}.html")
        output = st.text_input(t("csv_filename", interface_language), value="video_index.csv")
        command = build_video_command(
            folder_path,
            language=report_language,
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
        button_label=t("run_analysis", interface_language),
        interface_language=interface_language,
    )


def _render_organize_tab(st: Any, interface_language: str) -> None:
    organize_options = {
        t("organize_photos", interface_language): "photo",
        t("organize_videos", interface_language): "video",
    }
    organize_mode = st.radio(
        t("mode", interface_language),
        list(organize_options.keys()),
        horizontal=True,
    )
    st.warning(t("copy_recommended", interface_language))
    action_label = st.selectbox(
        t("mode_action", interface_language),
        [t("copy", interface_language), t("move", interface_language)],
        index=0,
    )
    action = "move" if action_label == t("move", interface_language) else "copy"

    if organize_options[organize_mode] == "photo":
        decisions_path = st.text_input(t("decisions_path", interface_language), value="decisions.csv")
        organize_output = st.text_input(t("output_folder", interface_language), value="organized_media")
        command = build_photo_organize_command(
            decisions_path,
            organize_output=organize_output,
            organize_mode=action,
        )
    else:
        decisions_path = st.text_input(t("decisions_path", interface_language), value="video_decisions.csv")
        organize_output = st.text_input(t("output_folder", interface_language), value="organized_videos")
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
        button_label=t("run_organize", interface_language),
        interface_language=interface_language,
    )


def _render_help_tab(st: Any, interface_language: str) -> None:
    st.subheader(t("basic_workflow", interface_language))
    st.markdown(
        "\n".join(
            [
                f"- {t('photo_workflow', interface_language)}",
                f"- {t('video_workflow', interface_language)}",
            ]
        )
    )

    st.subheader(t("cli_examples", interface_language))
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
    st.markdown(f"{t('github_repo', interface_language)}: [{GITHUB_REPO_URL}]({GITHUB_REPO_URL})")


def _render_run_button(
    st: Any,
    command: list[str],
    report_path_for_open: Path | None,
    open_report: bool,
    *,
    required_path: str,
    button_label: str,
    interface_language: str,
) -> None:
    st.subheader(t("final_command", interface_language))
    st.code(" ".join(command), language="bash")
    if not st.button(button_label):
        return

    if not required_path.strip():
        st.error(t("missing_path", interface_language))
        return

    with st.spinner("Running Media Agent..."):
        completed = run_command(command)

    if completed.returncode == 0:
        st.success(t("success", interface_language))
        result = parse_cli_output(completed.stdout)
        _render_result_summary(st, result, interface_language)
        _render_result_links(st, result, interface_language)
        if completed.stdout:
            with st.expander(t("show_stdout", interface_language)):
                st.code(completed.stdout)
        if report_path_for_open and open_report:
            webbrowser.open(report_path_for_open.as_uri())
            st.info(f"{t('report_opened', interface_language)} {report_path_for_open}")
    else:
        st.error(t("failed", interface_language))
        if completed.stdout:
            with st.expander(t("show_stdout", interface_language)):
                st.code(completed.stdout)
        if completed.stderr:
            with st.expander(t("show_stderr", interface_language), expanded=True):
                st.code(completed.stderr)


def _render_result_summary(st: Any, result: dict[str, str], interface_language: str) -> None:
    if not result:
        return
    labels = {
        "scanned": t("scanned", interface_language),
        "csv_path": t("csv_path", interface_language),
        "report_path": t("report_path", interface_language),
        "thumbnails_path": t("thumbnails_path", interface_language),
        "keyframes_path": t("keyframes_path", interface_language),
        "organized_path": t("organized_path", interface_language),
        "log_path": t("log_path", interface_language),
    }
    for key, label in labels.items():
        if key in result:
            st.write(f"**{label}:** `{result[key]}`")


def _render_result_links(st: Any, result: dict[str, str], interface_language: str) -> None:
    link_targets = [
        (t("open_report_link", interface_language), result.get("report_path")),
        (t("open_csv_link", interface_language), result.get("csv_path")),
        (t("open_thumbnails_link", interface_language), result.get("thumbnails_path")),
        (t("open_keyframes_link", interface_language), result.get("keyframes_path")),
        (t("open_organized_link", interface_language), result.get("organized_path")),
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

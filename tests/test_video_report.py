from __future__ import annotations

from pathlib import Path

from media_agent.video.report import export_video_html_report


def test_video_report_includes_review_controls_search_filter_and_export(tmp_path: Path) -> None:
    keyframe = tmp_path / "video_keyframes" / "demo" / "frame_001.jpg"
    keyframe.parent.mkdir(parents=True)
    keyframe.write_bytes(b"demo frame")
    report_path = tmp_path / "video_report.html"
    records = [
        {
            "filename": "demo_video.mp4",
            "file_path": "/media/demo_video.mp4",
            "duration_seconds": 3.2,
            "width": 1920,
            "height": 1080,
            "fps": 29.97,
            "codec": "h264",
            "keyframe_paths": [str(keyframe)],
            "avg_blur_score": 320.0,
            "avg_exposure_score": 92.0,
            "stability_score": 88.0,
            "avg_motion": 2.5,
            "max_motion": 4.2,
            "shaky_frame_count": 0,
            "stability_recommendation": "stable",
            "video_quality_recommendation": "keep",
            "recommendation_reason": "clear keyframes, good exposure",
        }
    ]

    export_video_html_report(records, report_path, language="en")

    html = report_path.read_text(encoding="utf-8")
    assert 'id="video-search"' in html
    assert 'id="recommendation-filter"' in html
    assert 'id="export-video-decisions"' in html
    assert 'data-decision="keep"' in html
    assert 'data-decision="review"' in html
    assert 'data-decision="reject"' in html
    assert 'data-video-quality-recommendation="keep"' in html
    assert 'data-file-path="/media/demo_video.mp4"' in html
    assert "media_agent_video_user_decisions_v1" in html
    assert "localStorage.setItem" in html
    assert "video_decisions.csv" in html
    assert '"video_quality_recommendation"' in html
    assert "filename.includes(query)" in html
    assert "recommendation-filter" in html
    assert "video_keyframes/demo/frame_001.jpg" in html
    assert "Stability Score" in html
    assert "Avg Motion" in html
    assert "Max Motion" in html
    assert "Shaky Frame Count" in html
    assert "Stability Recommendation" in html
    assert ">88<" in html
    assert ">stable<" in html

    zh_report_path = tmp_path / "video_report_zh.html"
    export_video_html_report(records, zh_report_path, language="zh")
    zh_html = zh_report_path.read_text(encoding="utf-8")
    assert "稳定性评分" in zh_html
    assert "平均运动量" in zh_html
    assert "最大运动量" in zh_html
    assert "抖动帧数" in zh_html
    assert "稳定性建议" in zh_html
    assert ">稳定<" in zh_html


def test_video_report_dashboard_includes_dataset_summary_and_percentages(tmp_path: Path) -> None:
    report_path = tmp_path / "dataset_report.html"
    records = [
        _dashboard_record(
            filename="keep_stable.mp4",
            duration_seconds=10,
            frame_count=2,
            width=1920,
            height=1080,
            fps=29.97,
            codec="h264",
            avg_blur_score=300,
            avg_exposure_score=90,
            stability_score=95,
            video_quality_recommendation="keep",
            stability_recommendation="stable",
        ),
        _dashboard_record(
            filename="review_moderate.mp4",
            duration_seconds=20,
            frame_count=3,
            width=1920,
            height=1080,
            fps=29.97,
            codec="h264",
            avg_blur_score=50,
            avg_exposure_score=85,
            stability_score=55,
            video_quality_recommendation="review",
            stability_recommendation="moderate",
        ),
        _dashboard_record(
            filename="reject_shaky.mp4",
            duration_seconds=30,
            frame_count=4,
            width=1280,
            height=720,
            fps=60,
            codec="hevc",
            avg_blur_score=100,
            avg_exposure_score=30,
            stability_score=30,
            video_quality_recommendation="reject_candidate",
            stability_recommendation="shaky",
        ),
    ]

    export_video_html_report(records, report_path, language="en")

    html = report_path.read_text(encoding="utf-8")
    assert "Total Duration" in html
    assert "Shortest Duration" in html
    assert "Longest Duration" in html
    assert "Average Keyframes per Video" in html
    assert "Recommendation Distribution" in html
    assert "Stability Distribution" in html
    assert "Most Common Resolution" in html
    assert "Most Common FPS" in html
    assert "Most Common Codec" in html
    assert "Average Stability Score" in html
    assert "Worst Blur Video" in html
    assert "Worst Exposure Video" in html
    assert "Shakiest Video" in html
    assert ">1:00<" in html
    assert ">0:20<" in html
    assert ">0:10<" in html
    assert ">0:30<" in html
    assert ">9<" in html
    assert ">3<" in html
    assert "1 (33.3%)" in html
    assert html.count("1 (33.3%)") >= 6
    assert ">1920 x 1080<" in html
    assert ">29.97<" in html
    assert ">h264<" in html
    assert ">50<" in html
    assert ">30<" in html
    assert ">60<" in html
    assert "review_moderate.mp4" in html
    assert "reject_shaky.mp4" in html


def test_video_report_dashboard_handles_empty_records(tmp_path: Path) -> None:
    report_path = tmp_path / "empty_video_report.html"

    export_video_html_report([], report_path, language="en")

    html = report_path.read_text(encoding="utf-8")
    assert "Total Videos" in html
    assert "Total Duration" in html
    assert "Recommendation Distribution" in html
    assert "Stability Distribution" in html
    assert "Most Common Resolution" in html
    assert "Worst Blur Video" in html
    assert "Shakiest Video" in html
    assert "0 (0%)" in html
    assert html.count("0 (0%)") >= 6


def test_video_report_dashboard_supports_chinese_labels(tmp_path: Path) -> None:
    report_path = tmp_path / "dataset_report_zh.html"
    records = [
        _dashboard_record(
            filename="keep_stable.mp4",
            duration_seconds=12,
            frame_count=2,
            width=3840,
            height=2160,
            fps=30,
            codec="h264",
            avg_blur_score=220,
            avg_exposure_score=88,
            stability_score=86,
            video_quality_recommendation="keep",
            stability_recommendation="stable",
        )
    ]

    export_video_html_report(records, report_path, language="zh")

    html = report_path.read_text(encoding="utf-8")
    assert "总视频时长" in html
    assert "推荐分布" in html
    assert "稳定性分布" in html
    assert "最常见分辨率" in html
    assert "最常见帧率" in html
    assert "最抖视频" in html
    assert "1 (100%)" in html


def _dashboard_record(
    *,
    filename: str,
    duration_seconds: float,
    frame_count: int,
    width: int,
    height: int,
    fps: float,
    codec: str,
    avg_blur_score: float,
    avg_exposure_score: float,
    stability_score: float,
    video_quality_recommendation: str,
    stability_recommendation: str,
) -> dict[str, object]:
    return {
        "filename": filename,
        "file_path": f"/media/{filename}",
        "duration_seconds": duration_seconds,
        "frame_count": frame_count,
        "width": width,
        "height": height,
        "fps": fps,
        "codec": codec,
        "keyframe_paths": [],
        "avg_blur_score": avg_blur_score,
        "avg_exposure_score": avg_exposure_score,
        "stability_score": stability_score,
        "avg_motion": 0.0,
        "max_motion": 0.0,
        "shaky_frame_count": 0,
        "stability_recommendation": stability_recommendation,
        "video_quality_recommendation": video_quality_recommendation,
        "recommendation_reason": "",
    }

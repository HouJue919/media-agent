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

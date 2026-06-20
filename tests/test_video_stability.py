from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from media_agent.video.stability import analyze_video_stability


def test_static_keyframes_have_high_stability_score(tmp_path: Path) -> None:
    frame = _demo_frame()
    first = tmp_path / "frame_001.jpg"
    second = tmp_path / "frame_002.jpg"
    _write_frame(first, frame)
    _write_frame(second, frame)

    result = analyze_video_stability([first, second])

    assert result["stability_score"] >= 95.0
    assert result["avg_motion"] <= 1.0
    assert result["stability_recommendation"] == "stable"


def test_changed_keyframes_have_lower_stability_score(tmp_path: Path) -> None:
    first = tmp_path / "frame_001.jpg"
    second = tmp_path / "frame_002.jpg"
    _write_frame(first, _demo_frame())
    _write_frame(second, 255 - _demo_frame())

    result = analyze_video_stability([first, second])

    assert result["stability_score"] < 80.0
    assert result["avg_motion"] > 5.0
    assert result["stability_recommendation"] in {"moderate", "shaky"}


def test_stability_falls_back_when_fewer_than_two_keyframes(tmp_path: Path) -> None:
    frame_path = tmp_path / "frame_001.jpg"
    _write_frame(frame_path, _demo_frame())

    result = analyze_video_stability([frame_path])

    assert result == {
        "stability_score": 100.0,
        "avg_motion": 0.0,
        "max_motion": 0.0,
        "shaky_frame_count": 0,
        "stability_recommendation": "stable",
    }


def _demo_frame() -> np.ndarray:
    frame = np.zeros((180, 240), dtype=np.uint8)
    cv2.rectangle(frame, (20, 20), (220, 160), 80, thickness=-1)
    for x in range(35, 210, 35):
        for y in range(35, 150, 35):
            cv2.circle(frame, (x, y), 6, 230, thickness=-1)
    cv2.line(frame, (20, 160), (220, 20), 180, thickness=3)
    return frame


def _write_frame(path: Path, frame: np.ndarray) -> None:
    success, encoded = cv2.imencode(".jpg", frame)
    assert success
    encoded.tofile(str(path))

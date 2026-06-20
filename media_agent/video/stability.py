from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np


MAX_STABILITY_SIZE = 480
STABLE_SCORE_THRESHOLD = 80.0
MODERATE_SCORE_THRESHOLD = 50.0
SHAKY_FRAME_MOTION_THRESHOLD = 18.0


def analyze_video_stability(frame_paths: list[Path]) -> dict[str, Any]:
    frames = [_load_grayscale_frame(path) for path in frame_paths]
    frames = [frame for frame in frames if frame is not None]
    if len(frames) < 2:
        return {
            "stability_score": 100.0,
            "avg_motion": 0.0,
            "max_motion": 0.0,
            "shaky_frame_count": 0,
            "stability_recommendation": "stable",
        }

    motions = [_estimate_motion(previous, current) for previous, current in zip(frames, frames[1:])]
    avg_motion = sum(motions) / len(motions) if motions else 0.0
    max_motion = max(motions) if motions else 0.0
    shaky_frame_count = sum(1 for motion in motions if motion >= SHAKY_FRAME_MOTION_THRESHOLD)
    stability_score = _score_stability(avg_motion, max_motion)

    return {
        "stability_score": round(stability_score, 2),
        "avg_motion": round(avg_motion, 2),
        "max_motion": round(max_motion, 2),
        "shaky_frame_count": shaky_frame_count,
        "stability_recommendation": _recommend_stability(stability_score),
    }


def _load_grayscale_frame(path: Path) -> np.ndarray | None:
    try:
        data = np.fromfile(str(path), dtype=np.uint8)
        image = cv2.imdecode(data, cv2.IMREAD_GRAYSCALE)
    except Exception:
        return None
    if image is None:
        return None
    return _resize_for_stability(image)


def _resize_for_stability(image: np.ndarray) -> np.ndarray:
    height, width = image.shape[:2]
    longest = max(width, height)
    if longest <= MAX_STABILITY_SIZE:
        return image
    scale = MAX_STABILITY_SIZE / longest
    new_size = (max(1, int(width * scale)), max(1, int(height * scale)))
    return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)


def _estimate_motion(previous: np.ndarray, current: np.ndarray) -> float:
    if previous.shape != current.shape:
        current = cv2.resize(current, (previous.shape[1], previous.shape[0]), interpolation=cv2.INTER_AREA)

    flow_motion = _estimate_optical_flow_motion(previous, current)
    difference_motion = _estimate_difference_motion(previous, current)
    return max(flow_motion, difference_motion)


def _estimate_optical_flow_motion(previous: np.ndarray, current: np.ndarray) -> float:
    points = cv2.goodFeaturesToTrack(previous, maxCorners=220, qualityLevel=0.01, minDistance=7)
    if points is None or len(points) < 8:
        return 0.0

    next_points, status, _ = cv2.calcOpticalFlowPyrLK(previous, current, points, None)
    if next_points is None or status is None:
        return 0.0

    valid_previous = points[status.flatten() == 1]
    valid_next = next_points[status.flatten() == 1]
    if len(valid_previous) < 8:
        return 0.0

    displacements = np.linalg.norm(valid_next.reshape(-1, 2) - valid_previous.reshape(-1, 2), axis=1)
    if displacements.size == 0:
        return 0.0

    upper = np.percentile(displacements, 90)
    trimmed = displacements[displacements <= upper]
    return float(np.mean(trimmed if trimmed.size else displacements))


def _estimate_difference_motion(previous: np.ndarray, current: np.ndarray) -> float:
    difference = cv2.absdiff(previous, current)
    normalized_difference = float(np.mean(difference)) / 255.0
    return normalized_difference * 60.0


def _score_stability(avg_motion: float, max_motion: float) -> float:
    score = 100.0 - (avg_motion * 3.0) - max(0.0, max_motion - SHAKY_FRAME_MOTION_THRESHOLD)
    return max(0.0, min(100.0, score))


def _recommend_stability(stability_score: float) -> str:
    if stability_score >= STABLE_SCORE_THRESHOLD:
        return "stable"
    if stability_score >= MODERATE_SCORE_THRESHOLD:
        return "moderate"
    return "shaky"

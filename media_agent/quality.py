from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image

try:
    from pillow_heif import register_heif_opener

    register_heif_opener()
except Exception:
    pass


MAX_ANALYSIS_SIZE = 1600
BLUR_THRESHOLD = 100.0
OVEREXPOSED_THRESHOLD = 250
UNDEREXPOSED_THRESHOLD = 5


def analyze_quality(path: Path) -> dict[str, Any]:
    try:
        image = _load_image_bgr(path)
        if image is None:
            raise ValueError("unsupported or unreadable image format")
        image = _resize_for_analysis(image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        overexposed_ratio = float(np.mean(gray >= OVEREXPOSED_THRESHOLD))
        underexposed_ratio = float(np.mean(gray <= UNDEREXPOSED_THRESHOLD))
        exposure_score = _score_exposure(overexposed_ratio, underexposed_ratio)
        blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        is_blurry = blur_score < BLUR_THRESHOLD
        waste_candidate = (
            is_blurry
            or overexposed_ratio > 0.20
            or underexposed_ratio > 0.30
            or exposure_score < 45
        )

        return {
            "exposure_score": round(exposure_score, 2),
            "overexposed_ratio": round(overexposed_ratio, 6),
            "underexposed_ratio": round(underexposed_ratio, 6),
            "blur_score": round(blur_score, 2),
            "is_blurry": is_blurry,
            "waste_candidate": waste_candidate,
            "quality_error": None,
        }
    except Exception as exc:
        return {
            "exposure_score": None,
            "overexposed_ratio": None,
            "underexposed_ratio": None,
            "blur_score": None,
            "is_blurry": None,
            "waste_candidate": None,
            "quality_error": str(exc),
        }


def _load_image_bgr(path: Path) -> np.ndarray | None:
    image = _load_with_opencv(path)
    if image is not None:
        return image
    return _load_with_pillow(path)


def _load_with_opencv(path: Path) -> np.ndarray | None:
    try:
        data = np.fromfile(str(path), dtype=np.uint8)
        return cv2.imdecode(data, cv2.IMREAD_COLOR)
    except Exception:
        return None


def _load_with_pillow(path: Path) -> np.ndarray | None:
    try:
        with Image.open(path) as image:
            rgb = image.convert("RGB")
            array = np.array(rgb)
            return cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
    except Exception:
        return None


def _resize_for_analysis(image: np.ndarray) -> np.ndarray:
    height, width = image.shape[:2]
    longest = max(width, height)
    if longest <= MAX_ANALYSIS_SIZE:
        return image
    scale = MAX_ANALYSIS_SIZE / longest
    new_size = (int(width * scale), int(height * scale))
    return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)


def _score_exposure(overexposed_ratio: float, underexposed_ratio: float) -> float:
    penalty = overexposed_ratio * 180 + underexposed_ratio * 140
    return max(0.0, min(100.0, 100.0 - penalty))

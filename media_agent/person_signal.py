from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np


MAX_DETECTION_SIZE = 900

DEFAULT_PERSON_SIGNAL = {
    "face_detected": False,
    "face_count": 0,
    "person_signal": False,
    "person_signal_confidence": 0.0,
    "person_signal_method": "none",
}


def detect_person_signal(path: Path | str | None) -> dict[str, Any]:
    """Detect whether an image may contain a face/person signal.

    This is intentionally not identity recognition. It only returns a local
    computer-vision signal that memory-safe recommendations can use to avoid
    over-rejecting potentially meaningful photos.
    """
    if not path:
        return dict(DEFAULT_PERSON_SIGNAL)

    try:
        image = _load_image_bgr(Path(path))
        if image is None:
            return dict(DEFAULT_PERSON_SIGNAL)

        image = _resize_for_detection(image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face_count = _detect_face_count(gray)
        if face_count > 0:
            return {
                "face_detected": True,
                "face_count": face_count,
                "person_signal": True,
                "person_signal_confidence": _face_confidence(face_count),
                "person_signal_method": "haar_face",
            }
    except Exception:
        return dict(DEFAULT_PERSON_SIGNAL)

    return dict(DEFAULT_PERSON_SIGNAL)


def _load_image_bgr(path: Path) -> np.ndarray | None:
    try:
        data = np.fromfile(str(path), dtype=np.uint8)
        return cv2.imdecode(data, cv2.IMREAD_COLOR)
    except Exception:
        return None


def _resize_for_detection(image: np.ndarray) -> np.ndarray:
    height, width = image.shape[:2]
    longest = max(width, height)
    if longest <= MAX_DETECTION_SIZE:
        return image
    scale = MAX_DETECTION_SIZE / longest
    new_size = (max(1, int(width * scale)), max(1, int(height * scale)))
    return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)


def _detect_face_count(gray: np.ndarray) -> int:
    cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    cascade = cv2.CascadeClassifier(str(cascade_path))
    if cascade.empty():
        return 0
    faces = cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(24, 24),
    )
    return int(len(faces))


def _face_confidence(face_count: int) -> float:
    return round(min(0.95, 0.55 + min(face_count, 3) * 0.15), 2)

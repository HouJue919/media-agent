from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from media_agent.person_signal import detect_person_signal


def test_synthetic_image_without_face_has_no_person_signal(tmp_path: Path) -> None:
    image_path = tmp_path / "no_face.jpg"
    image = Image.new("RGB", (180, 140), "black")
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 20, 160, 120), outline="white", width=3)
    draw.line((20, 120, 160, 20), fill="white", width=2)
    image.save(image_path)

    result = detect_person_signal(image_path)

    assert result["face_detected"] is False
    assert result["face_count"] == 0
    assert result["person_signal"] is False
    assert result["person_signal_confidence"] == 0.0
    assert result["person_signal_method"] == "none"


def test_unreadable_image_returns_default_person_signal(tmp_path: Path) -> None:
    image_path = tmp_path / "not_an_image.jpg"
    image_path.write_text("not image data", encoding="utf-8")

    result = detect_person_signal(image_path)

    assert result["face_detected"] is False
    assert result["face_count"] == 0
    assert result["person_signal"] is False
    assert result["person_signal_confidence"] == 0.0
    assert result["person_signal_method"] == "none"

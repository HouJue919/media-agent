from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from media_agent.similarity import annotate_duplicate_groups


def test_similar_images_enter_same_duplicate_group(tmp_path: Path) -> None:
    first = tmp_path / "first.jpg"
    second = tmp_path / "second.jpg"
    image = _pattern_image()
    image.save(first)
    image.save(second)
    records = [{"path": str(first)}, {"path": str(second)}]

    annotate_duplicate_groups(records, distance_threshold=0)

    assert records[0]["duplicate_group_id"] == records[1]["duplicate_group_id"]
    assert records[0]["duplicate_count"] == 2
    assert records[1]["is_duplicate_candidate"] is True


def test_different_images_do_not_group_with_exact_threshold(tmp_path: Path) -> None:
    first = tmp_path / "first.jpg"
    second = tmp_path / "second.jpg"
    _pattern_image().save(first)
    _different_pattern_image().save(second)
    records = [{"path": str(first)}, {"path": str(second)}]

    annotate_duplicate_groups(records, distance_threshold=0)

    assert records[0]["duplicate_group_id"] is None
    assert records[1]["duplicate_group_id"] is None
    assert records[0]["is_duplicate_candidate"] is False
    assert records[1]["is_duplicate_candidate"] is False


def _pattern_image() -> Image.Image:
    image = Image.new("RGB", (128, 128), (90, 140, 190))
    draw = ImageDraw.Draw(image)
    draw.rectangle((8, 8, 70, 70), fill=(230, 210, 120))
    draw.ellipse((50, 40, 116, 112), fill=(40, 90, 70))
    draw.line((0, 120, 128, 15), fill=(250, 250, 245), width=4)
    return image


def _different_pattern_image() -> Image.Image:
    image = Image.new("RGB", (128, 128), (28, 34, 48))
    draw = ImageDraw.Draw(image)
    for x in range(0, 128, 16):
        color = (180, 70, 60) if x % 32 == 0 else (55, 160, 130)
        draw.rectangle((x, 0, x + 8, 128), fill=color)
    draw.polygon([(20, 105), (64, 12), (108, 105)], fill=(240, 240, 230))
    return image

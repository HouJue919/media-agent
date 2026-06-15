from __future__ import annotations

import contextlib
import io
from datetime import datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import exifread
from PIL import ExifTags, Image

try:
    from pillow_heif import register_heif_opener

    register_heif_opener()
except Exception:
    pass


PIL_TAGS = {value: key for key, value in ExifTags.TAGS.items()}


def build_media_record(path: Path) -> dict[str, Any]:
    stat = path.stat()
    metadata = {
        "filename": path.name,
        "path": str(path),
        "file_size_bytes": stat.st_size,
        "created_at": _format_timestamp(stat.st_birthtime if hasattr(stat, "st_birthtime") else stat.st_ctime),
        "modified_at": _format_timestamp(stat.st_mtime),
        "width": None,
        "height": None,
        "camera_model": None,
        "lens_model": None,
        "focal_length": None,
        "aperture": None,
        "shutter_speed": None,
        "iso": None,
        "taken_at": None,
    }

    pil_data = _read_with_pillow(path)
    if pil_data:
        metadata.update({key: value for key, value in pil_data.items() if value is not None})

    exifread_data = _read_with_exifread(path)
    for key, value in exifread_data.items():
        if metadata.get(key) in (None, "") and value not in (None, ""):
            metadata[key] = value

    return metadata


def _format_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).isoformat(timespec="seconds")


def _read_with_pillow(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {}
    try:
        with Image.open(path) as image:
            result["width"], result["height"] = image.size
            exif = image.getexif()
            if not exif:
                return result

            result["camera_model"] = _clean_text(exif.get(PIL_TAGS.get("Model")))
            result["lens_model"] = _clean_text(exif.get(PIL_TAGS.get("LensModel")))
            result["focal_length"] = _format_number(exif.get(PIL_TAGS.get("FocalLength")))
            result["aperture"] = _format_f_number(exif.get(PIL_TAGS.get("FNumber")))
            result["shutter_speed"] = _format_shutter(exif.get(PIL_TAGS.get("ExposureTime")))
            result["iso"] = _format_number(exif.get(PIL_TAGS.get("ISOSpeedRatings")))
            result["taken_at"] = _format_exif_datetime(
                exif.get(PIL_TAGS.get("DateTimeOriginal"))
                or exif.get(PIL_TAGS.get("DateTimeDigitized"))
                or exif.get(PIL_TAGS.get("DateTime"))
            )
    except Exception:
        return result
    return result


def _read_with_exifread(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as file:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                tags = exifread.process_file(file, details=False, stop_tag="UNDEF")
    except Exception:
        return {}

    width = _first_tag(tags, "EXIF ExifImageWidth", "Image ImageWidth")
    height = _first_tag(tags, "EXIF ExifImageLength", "Image ImageLength")
    return {
        "width": _to_int(width),
        "height": _to_int(height),
        "camera_model": _clean_text(_first_tag(tags, "Image Model")),
        "lens_model": _clean_text(_first_tag(tags, "EXIF LensModel", "MakerNote LensType")),
        "focal_length": _format_number(_first_tag(tags, "EXIF FocalLength")),
        "aperture": _format_f_number(_first_tag(tags, "EXIF FNumber")),
        "shutter_speed": _format_shutter(_first_tag(tags, "EXIF ExposureTime")),
        "iso": _format_number(_first_tag(tags, "EXIF ISOSpeedRatings", "EXIF PhotographicSensitivity")),
        "taken_at": _format_exif_datetime(
            _first_tag(tags, "EXIF DateTimeOriginal", "Image DateTime", "EXIF DateTimeDigitized")
        ),
    }


def _first_tag(tags: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in tags:
            return tags[name]
    return None


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip().replace("\x00", "")
    return text or None


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _format_number(value: Any) -> str | None:
    if value is None:
        return None
    try:
        if isinstance(value, tuple) and len(value) == 2:
            number = Fraction(value[0], value[1])
        elif hasattr(value, "numerator") and hasattr(value, "denominator"):
            number = Fraction(value.numerator, value.denominator)
        else:
            text = str(value).strip()
            if "/" in text:
                number = Fraction(text)
            else:
                parsed = float(text)
                return str(int(parsed)) if parsed.is_integer() else f"{parsed:.2f}".rstrip("0").rstrip(".")
        parsed = float(number)
        return str(int(parsed)) if parsed.is_integer() else f"{parsed:.2f}".rstrip("0").rstrip(".")
    except Exception:
        text = str(value).strip()
        return text or None


def _format_f_number(value: Any) -> str | None:
    number = _format_number(value)
    return f"f/{number}" if number else None


def _format_shutter(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if "/" in text:
        return text
    try:
        parsed = float(text)
    except ValueError:
        return text or None
    if parsed <= 0:
        return None
    if parsed < 1:
        denominator = round(1 / parsed)
        return f"1/{denominator}"
    return f"{parsed:.2f}s".rstrip("0").rstrip(".")


def _format_exif_datetime(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt).isoformat(timespec="seconds")
        except ValueError:
            continue
    return text or None

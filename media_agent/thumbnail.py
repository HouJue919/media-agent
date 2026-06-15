from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageOps

try:
    from pillow_heif import register_heif_opener

    register_heif_opener()
except Exception:
    pass


THUMBNAIL_SIZE = (320, 320)


def create_thumbnail(source_path: Path, thumbnail_dir: Path, size: tuple[int, int] = THUMBNAIL_SIZE) -> Path | None:
    thumbnail_dir.mkdir(parents=True, exist_ok=True)
    output_path = thumbnail_dir / _thumbnail_filename(source_path)

    try:
        with Image.open(source_path) as image:
            image = ImageOps.exif_transpose(image)
            image.thumbnail(size, Image.Resampling.LANCZOS)
            image = _flatten_to_rgb(image)
            image.save(output_path, format="JPEG", quality=85, optimize=True)
    except Exception:
        return None

    return output_path


def _thumbnail_filename(source_path: Path) -> str:
    digest = hashlib.sha1(str(source_path).encode("utf-8")).hexdigest()[:12]
    safe_stem = "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in source_path.stem)
    return f"{safe_stem}_{digest}.jpg"


def _flatten_to_rgb(image: Image.Image) -> Image.Image:
    if image.mode == "RGB":
        return image
    if image.mode in ("RGBA", "LA") or "transparency" in image.info:
        background = Image.new("RGB", image.size, (255, 255, 255))
        alpha = image.convert("RGBA").getchannel("A")
        background.paste(image.convert("RGB"), mask=alpha)
        return background
    return image.convert("RGB")

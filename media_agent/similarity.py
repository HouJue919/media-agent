from __future__ import annotations

from pathlib import Path
from typing import Any

import imagehash
from PIL import Image, ImageOps

try:
    from pillow_heif import register_heif_opener

    register_heif_opener()
except Exception:
    pass


PHASH_DISTANCE_THRESHOLD = 6


def annotate_duplicate_groups(
    records: list[dict[str, Any]],
    distance_threshold: int = PHASH_DISTANCE_THRESHOLD,
) -> list[dict[str, Any]]:
    hashes: list[str | None] = []
    for record in records:
        phash = compute_phash(Path(str(record.get("path"))))
        record["phash"] = phash
        hashes.append(phash)

    parent = list(range(len(records)))

    for left_index in range(len(records)):
        left_hash = hashes[left_index]
        if not left_hash:
            continue
        for right_index in range(left_index + 1, len(records)):
            right_hash = hashes[right_index]
            if not right_hash:
                continue
            if hamming_distance(left_hash, right_hash) <= distance_threshold:
                _union(parent, left_index, right_index)

    components: dict[int, list[int]] = {}
    for index, phash in enumerate(hashes):
        if not phash:
            records[index]["duplicate_group_id"] = None
            records[index]["duplicate_count"] = 0
            records[index]["is_duplicate_candidate"] = False
            continue
        root = _find(parent, index)
        components.setdefault(root, []).append(index)

    duplicate_components = [indices for indices in components.values() if len(indices) > 1]
    duplicate_components.sort(key=lambda indices: min(indices))
    group_ids = {
        min(indices): f"dup_{group_number:03d}"
        for group_number, indices in enumerate(duplicate_components, start=1)
    }

    for indices in components.values():
        duplicate_count = len(indices)
        group_id = group_ids.get(min(indices)) if duplicate_count > 1 else None
        for index in indices:
            records[index]["duplicate_group_id"] = group_id
            records[index]["duplicate_count"] = duplicate_count
            records[index]["is_duplicate_candidate"] = duplicate_count > 1

    return records


def compute_phash(path: Path) -> str | None:
    try:
        with Image.open(path) as image:
            image = ImageOps.exif_transpose(image)
            return str(imagehash.phash(image))
    except Exception:
        return None


def hamming_distance(left_hash: str, right_hash: str) -> int:
    return (int(left_hash, 16) ^ int(right_hash, 16)).bit_count()


def _find(parent: list[int], index: int) -> int:
    while parent[index] != index:
        parent[index] = parent[parent[index]]
        index = parent[index]
    return index


def _union(parent: list[int], left_index: int, right_index: int) -> None:
    left_root = _find(parent, left_index)
    right_root = _find(parent, right_index)
    if left_root != right_root:
        parent[right_root] = left_root

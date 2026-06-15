# v0.1.0 Portfolio Release

## Release name

v0.1.0 Portfolio Release

## Summary

Media Agent is an AI-assisted visual asset management system for photographers and content creators.

This first portfolio release packages the project as a complete, local-first Python workflow for photo review. It scans image folders, extracts metadata, evaluates basic visual quality, detects duplicate or similar photos, recommends keep/review/reject decisions, generates an interactive HTML report, and supports safe post-review file organization.

The release is designed for GitHub and portfolio presentation. It includes a public synthetic demo dataset, reproducible demo generation script, README screenshots, MIT License, and a focused pytest suite.

## Key Features

- Photo scanning for JPG, JPEG, PNG, HEIC, and ARW files.
- File metadata and EXIF extraction, including camera, lens, focal length, aperture, shutter speed, ISO, and capture time.
- Traditional computer vision quality analysis for blur, exposure, overexposure, and underexposure.
- Thumbnail generation for report review.
- Perceptual hash based duplicate and similar photo detection.
- Best-pick recommendation inside duplicate groups.
- Keep, review, and reject-candidate recommendation workflow.
- Recommendation reasons for transparent review.
- Static HTML report with dashboard summary metrics.
- Browser localStorage based manual decision workflow.
- `decisions.csv` export for human-in-the-loop review.
- Safe file organization by copy or move, with no delete mode.
- English and Chinese report support.
- Mock/local AI tagging architecture with no external API calls.

## Demo Dataset

This release includes `demo_media/`, a synthetic public dataset generated with Python and Pillow. It does not contain private photos.

The dataset covers:

- normal sharp image
- blurry image
- overexposed image
- underexposed image
- duplicate/similar pair
- Fuji mountain keyword image
- sunset sky keyword image
- Tokyo street keyword image
- plane airport keyword image
- unknown image

The demo dataset can be regenerated with:

```bash
python scripts/generate_demo_media.py
```

The demo report can be generated with:

```bash
python main.py demo_media --language en --report demo_report.html --enable-ai-tags --ai-provider mock
```

Generated outputs such as `demo_report.html`, `media_index.csv`, and `thumbnails/` are ignored by Git.

## Testing

The release includes pytest coverage for:

- scanner extension handling and `.DS_Store` ignoring
- perceptual-hash duplicate grouping
- best-pick ranking in duplicate groups
- safe organize copy mode
- duplicate filename collision handling

Validation commands:

```bash
python3 -m compileall -q main.py media_agent
python scripts/generate_demo_media.py
python main.py demo_media --language en --report demo_report.html --enable-ai-tags --ai-provider mock
pytest
```

Current validation result for this release:

- demo dataset generated successfully
- demo report generated successfully
- 8 pytest tests passed

## Current Limitations

- Mock AI tagging does not inspect actual image pixels. It uses file names, paths, metadata, and existing recommendation fields.
- No external AI API is connected in this release.
- Quality scoring uses heuristic thresholds and may need tuning for different cameras or shooting styles.
- RAW/ARW support depends on local decoding and metadata availability.
- Duplicate detection uses perceptual hashing and may not catch every near-duplicate.
- The HTML report is static and stores manual decisions in browser localStorage.

## Future Roadmap

- Add optional real vision model providers after the local workflow remains stable.
- Support local CLIP, BLIP, YOLO, or OpenAI Vision as replaceable providers.
- Add video support with `ffmpeg` frame extraction.
- Add report filters for recommendation, duplicate group, scene type, and AI tags.
- Add configurable quality thresholds.
- Add larger automated test coverage for report generation and CLI behavior.
- Package the project as a desktop-friendly tool for non-technical users.

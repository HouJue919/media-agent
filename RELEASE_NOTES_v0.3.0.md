# v0.3.0 Creator Workflow Release

## Release Name

v0.3.0 Creator Workflow Release

## Summary

Media Agent is now a photo and video asset management system for creators.

This release consolidates the photo workflow, video keyframe workflow, memory-safe recommendation logic, local face/person signal detection, static HTML reports, and safe organization tools into one local-first creator review pipeline.

The project remains non-destructive and does not call external AI APIs. All recommendations are designed as review priorities, not automatic deletion decisions.

## Key Features

- Photo scanning, metadata extraction, EXIF processing, thumbnail generation, and CSV export.
- Exposure and blur quality analysis using traditional computer vision.
- Duplicate and similar photo detection with perceptual hashing.
- Best-pick recommendation for duplicate groups.
- Memory-safe recommendation logic that separates technical quality from possible personal or story value.
- Local face/person signal detection using OpenCV Haar Cascade detection.
- Mock/local AI tagging architecture with no external API calls.
- Interactive bilingual HTML photo report with dashboard metrics, manual decisions, localStorage persistence, and `decisions.csv` export.
- Keyframe-based video analysis using `ffmpeg` and `ffprobe`.
- Video report review workflow with search, filters, sorting, priority review controls, and `video_decisions.csv` export.
- Safe photo and video organization workflows using copy-by-default behavior.

## v0.2.0 to v0.2.9 Highlights

### Video Keyframe Analysis

- Added video scanning for `.mp4`, `.mov`, and `.m4v`.
- Added `ffprobe` metadata extraction.
- Added `ffmpeg` keyframe extraction.
- Reused the existing image quality pipeline for keyframes.
- Generated `video_index.csv` and bilingual `video_report.html`.

### Video Report Review Workflow

- Added keep, review, and reject controls to `video_report.html`.
- Stored manual decisions in browser `localStorage`.
- Added `video_decisions.csv` export.
- Added filename search and recommendation filtering.

### Safe Video Organization

- Added `media_agent/video/organize.py`.
- Organized videos into selected keep, review, and reject folders.
- Defaulted to copy mode and avoided destructive delete operations.
- Prevented duplicate filename overwrites.
- Generated `video_organize_log.csv`.

### Video Stability Scoring

- Added OpenCV-based keyframe motion analysis.
- Added stability score, average motion, maximum motion, shaky frame count, and stability recommendation fields.
- Included stability signals in video recommendations and reports.

### Video Dataset Dashboard

- Expanded the video report dashboard for whole-batch review.
- Added duration statistics, keyframe statistics, recommendation distribution, stability distribution, common technical specs, and quality highlights.

### Video Priority Filtering and Sorting

- Added browser-side sorting controls.
- Added priority filters for review candidates, likely rejects, shaky videos, low sharpness, exposure problems, and long videos.
- Combined search, recommendation filtering, priority filtering, and sorting in the same static report.

### Local Report Preview Server

- Added `scripts/serve_report.py`.
- Recommended local HTTP preview for static HTML reports instead of relying on `file://`.
- Improved validation of report interactions such as localStorage and CSV export.

### Memory-Safe Recommendation Logic

- Added `technical_recommendation`, `final_recommendation`, `memory_risk`, `memory_risk_reason`, and `content_safety_override`.
- Kept `keep_recommendation` compatible by mapping it to the final memory-safe recommendation.
- Reduced over-aggressive rejection of people, selfie, travel, expression, and duplicate-moment photos.

### Local Face / Person Signal Detection

- Added local OpenCV Haar Cascade face detection.
- Added `face_detected`, `face_count`, `person_signal`, `person_signal_confidence`, and `person_signal_method`.
- Integrated local person signals into memory-safe review logic.
- This is not face recognition and does not identify people.

## Testing

Validation commands:

```bash
python3 -m compileall -q main.py media_agent scripts
pytest
```

Current validation result:

- Compile check passed.
- Pytest suite passed.

## Current Limitations

- Mock AI tagging does not inspect real image content.
- Face/person signal detection is a conservative local signal, not identity recognition.
- Video analysis is based on sampled keyframes and does not perform full semantic video understanding.
- Quality thresholds are heuristic and may require tuning for specific cameras or workflows.
- Static reports store manual choices in browser-local storage.

## Future Roadmap

- v0.3.x: Better UI polish and a real-world creator case study.
- v0.4.0: Local CLIP integration and visual semantic search.
- v0.5.0: Real AI scene tagging with replaceable providers.
- Longer-term: richer video scene analysis, shot detection, project profiles, larger media indexing, and desktop-friendly packaging.

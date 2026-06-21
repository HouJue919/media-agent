# Local Report Preview

Media Agent reports are static HTML files with JavaScript for search, sorting, filters, localStorage decisions, and CSV export.

Opening a report directly with `file://` can trigger browser security restrictions in some environments. The recommended preview workflow is to serve the report folder through a local HTTP server.

## Start the Preview Server

From the project root:

```bash
python scripts/serve_report.py --directory . --port 8000
```

If your report is inside an output folder:

```bash
python scripts/serve_report.py --directory test_outputs/video_sort_priority_demo --port 8000
```

The script prints URLs such as:

```text
http://localhost:8000/video_report.html
```

## Open the Report

Open the printed report URL in a browser.

For a video report, verify:

- Search by filename
- Recommendation filtering
- Priority Review filtering
- Sort By controls
- keep, review, and reject buttons
- `video_decisions.csv` export

## Stop the Server

Return to the terminal running the server and press:

```text
Ctrl+C
```

The server only serves local files from the selected directory. It does not upload media, delete files, or call external APIs.

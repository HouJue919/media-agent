from __future__ import annotations

import os
from collections import Counter
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any


RECOMMENDATION_ORDER = {
    "reject_candidate": 0,
    "review": 1,
    "keep": 2,
}
LOW_SHARPNESS_THRESHOLD = 80.0


TRANSLATIONS = {
    "zh": {
        "html_lang": "zh-CN",
        "title": "Media Agent 视频报告",
        "heading": "Media Agent 视频报告",
        "summary": "共 {count} 个视频，基于关键帧质量分析生成。",
        "dashboard_label": "视频统计摘要",
        "total_videos": "总视频数量",
        "total_duration": "总视频时长",
        "keep_count": "推荐保留",
        "review_count": "推荐复查",
        "reject_count": "删除候选",
        "average_duration": "平均时长",
        "shortest_duration": "最短时长",
        "longest_duration": "最长时长",
        "average_keyframes": "平均关键帧数",
        "recommendation_distribution": "推荐分布",
        "stability_distribution": "稳定性分布",
        "technical_summary": "技术规格统计",
        "quality_summary": "质量统计",
        "most_common_resolution": "最常见分辨率",
        "most_common_fps": "最常见帧率",
        "most_common_codec": "最常见编码",
        "average_blur": "平均清晰度",
        "average_exposure": "平均曝光",
        "average_stability": "平均稳定性",
        "worst_blur_video": "最模糊视频",
        "worst_exposure_video": "曝光最差视频",
        "shakiest_video": "最抖视频",
        "total_keyframes": "关键帧总数",
        "generated_at": "报告生成时间",
        "review_tools": "视频复查工具",
        "search": "搜索",
        "search_placeholder": "按文件名搜索",
        "filter_recommendation": "筛选建议",
        "all_recommendations": "全部建议",
        "sort_by": "排序",
        "sort_default": "默认",
        "sort_recommendation": "系统建议",
        "sort_duration_longest": "时长最长",
        "sort_duration_shortest": "时长最短",
        "sort_blur_worst": "清晰度最差",
        "sort_exposure_worst": "曝光最差",
        "sort_stability_worst": "稳定性最差",
        "sort_shaky_frames": "抖动帧数",
        "sort_keyframes": "关键帧数量",
        "priority_review": "优先复查",
        "priority_all": "全部",
        "priority_needs_review": "需要复查",
        "priority_likely_reject": "疑似废片",
        "priority_shaky": "抖动视频",
        "priority_low_sharpness": "清晰度较低",
        "priority_exposure": "曝光问题",
        "priority_long": "长视频",
        "export_decisions": "导出视频人工选择结果",
        "filename": "视频文件名",
        "duration": "时长",
        "resolution": "分辨率",
        "fps": "FPS",
        "codec": "编码",
        "keyframes": "关键帧预览",
        "avg_blur": "平均清晰度",
        "avg_exposure": "平均曝光",
        "stability_score": "稳定性评分",
        "avg_motion": "平均运动量",
        "max_motion": "最大运动量",
        "shaky_frame_count": "抖动帧数",
        "stability_recommendation": "稳定性建议",
        "recommendation": "系统建议",
        "reason": "推荐原因",
        "user_decision": "人工决定",
        "no_keyframes": "无关键帧",
        "stable": "稳定",
        "moderate": "中等",
        "shaky": "抖动",
        "keep": "保留",
        "review": "复查",
        "reject": "剔除",
        "reject_candidate": "删除候选",
    },
    "en": {
        "html_lang": "en",
        "title": "Media Agent Video Report",
        "heading": "Media Agent Video Report",
        "summary": "{count} videos analyzed with keyframe quality scoring.",
        "dashboard_label": "Video Summary Dashboard",
        "total_videos": "Total Videos",
        "total_duration": "Total Duration",
        "keep_count": "Keep",
        "review_count": "Review",
        "reject_count": "Reject Candidates",
        "average_duration": "Average Duration",
        "shortest_duration": "Shortest Duration",
        "longest_duration": "Longest Duration",
        "average_keyframes": "Average Keyframes per Video",
        "recommendation_distribution": "Recommendation Distribution",
        "stability_distribution": "Stability Distribution",
        "technical_summary": "Technical Summary",
        "quality_summary": "Quality Summary",
        "most_common_resolution": "Most Common Resolution",
        "most_common_fps": "Most Common FPS",
        "most_common_codec": "Most Common Codec",
        "average_blur": "Average Blur Score",
        "average_exposure": "Average Exposure Score",
        "average_stability": "Average Stability Score",
        "worst_blur_video": "Worst Blur Video",
        "worst_exposure_video": "Worst Exposure Video",
        "shakiest_video": "Shakiest Video",
        "total_keyframes": "Total Keyframes",
        "generated_at": "Report Generated At",
        "review_tools": "Video Review Tools",
        "search": "Search",
        "search_placeholder": "Search by filename",
        "filter_recommendation": "Filter Recommendation",
        "all_recommendations": "All Recommendations",
        "sort_by": "Sort By",
        "sort_default": "Default",
        "sort_recommendation": "Recommendation",
        "sort_duration_longest": "Duration Longest",
        "sort_duration_shortest": "Duration Shortest",
        "sort_blur_worst": "Blur Score Worst",
        "sort_exposure_worst": "Exposure Score Worst",
        "sort_stability_worst": "Stability Score Worst",
        "sort_shaky_frames": "Shaky Frame Count",
        "sort_keyframes": "Keyframe Count",
        "priority_review": "Priority Review",
        "priority_all": "All",
        "priority_needs_review": "Needs Review",
        "priority_likely_reject": "Likely Reject",
        "priority_shaky": "Shaky Videos",
        "priority_low_sharpness": "Low Sharpness",
        "priority_exposure": "Exposure Problems",
        "priority_long": "Long Videos",
        "export_decisions": "Export Video Decisions",
        "filename": "Video Filename",
        "duration": "Duration",
        "resolution": "Resolution",
        "fps": "FPS",
        "codec": "Codec",
        "keyframes": "Keyframe Preview",
        "avg_blur": "Average Blur",
        "avg_exposure": "Average Exposure",
        "stability_score": "Stability Score",
        "avg_motion": "Avg Motion",
        "max_motion": "Max Motion",
        "shaky_frame_count": "Shaky Frame Count",
        "stability_recommendation": "Stability Recommendation",
        "recommendation": "Recommendation",
        "reason": "Recommendation Reason",
        "user_decision": "User Decision",
        "no_keyframes": "No keyframes",
        "stable": "stable",
        "moderate": "moderate",
        "shaky": "shaky",
        "keep": "keep",
        "review": "review",
        "reject": "reject",
        "reject_candidate": "reject_candidate",
    },
}


def sort_video_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(records, key=_sort_key)


def export_video_html_report(records: list[dict[str, Any]], output_path: Path, language: str = "zh") -> None:
    t = _translations(language)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard = _build_dashboard(records)
    rows = "\n".join(_render_row(record, output_path.parent, t, index) for index, record in enumerate(records))
    output_path.write_text(_render_page(rows, len(records), dashboard, t), encoding="utf-8")


def _translations(language: str) -> dict[str, str]:
    return TRANSLATIONS.get(language, TRANSLATIONS["zh"])


def _sort_key(record: dict[str, Any]) -> tuple[int, float, float, str]:
    recommendation = str(record.get("video_quality_recommendation") or "")
    avg_blur = _number_or_default(record.get("avg_blur_score"), float("inf"))
    filename = str(record.get("filename") or "").lower()
    stability_score = _number_or_default(record.get("stability_score"), 100.0)
    return (RECOMMENDATION_ORDER.get(recommendation, 1), stability_score, avg_blur, filename)


def _build_dashboard(records: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(str(record.get("video_quality_recommendation") or "") for record in records)
    stability_counts = Counter(str(record.get("stability_recommendation") or "") for record in records)
    durations = [_number_or_none(record.get("duration_seconds")) for record in records]
    durations = [duration for duration in durations if duration is not None]
    total_keyframes = sum(_int_or_default(record.get("frame_count"), 0) for record in records)
    return {
        "total": len(records),
        "counts": counts,
        "stability_counts": stability_counts,
        "total_duration": sum(durations) if durations else None,
        "average_duration": _average(record.get("duration_seconds") for record in records),
        "shortest_duration": min(durations) if durations else None,
        "longest_duration": max(durations) if durations else None,
        "average_keyframes": (total_keyframes / len(records)) if records else None,
        "average_blur_score": _average(record.get("avg_blur_score") for record in records),
        "average_exposure_score": _average(record.get("avg_exposure_score") for record in records),
        "average_stability_score": _average(record.get("stability_score") for record in records),
        "total_keyframes": total_keyframes,
        "most_common_resolution": _most_common(_resolution_value(record) for record in records),
        "most_common_fps": _most_common(_fps_value(record) for record in records),
        "most_common_codec": _most_common(str(record.get("codec") or "").strip() for record in records),
        "worst_blur_video": _filename_for_lowest(records, "avg_blur_score"),
        "worst_exposure_video": _filename_for_lowest(records, "avg_exposure_score"),
        "shakiest_video": _filename_for_lowest(records, "stability_score"),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


def _render_page(rows: str, count: int, dashboard: dict[str, Any], t: dict[str, str]) -> str:
    summary_cards = _render_dashboard_cards(dashboard, t)
    return f"""<!doctype html>
<html lang="{t["html_lang"]}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{t["title"]}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --text: #1f2933;
      --muted: #64748b;
      --border: #d8dee6;
      --danger: #b42318;
      --ok: #067647;
      --warning: #b54708;
      --focus: #2563eb;
    }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 14px;
    }}
    header {{
      padding: 24px 28px 14px;
    }}
    h1 {{
      margin: 0 0 6px;
      font-size: 24px;
      font-weight: 700;
      letter-spacing: 0;
    }}
    .summary {{
      margin: 0;
      color: var(--muted);
    }}
    .dashboard {{
      padding: 0 28px 18px;
    }}
    .dashboard h2 {{
      margin: 0 0 10px;
      font-size: 16px;
      letter-spacing: 0;
    }}
    .dashboard-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 10px;
    }}
    .dashboard-section-title {{
      grid-column: 1 / -1;
      margin-top: 8px;
      color: #334155;
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
    }}
    .dashboard-card {{
      padding: 12px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
    }}
    .dashboard-label {{
      display: block;
      color: var(--muted);
      font-size: 12px;
    }}
    .dashboard-value {{
      display: block;
      margin-top: 4px;
      font-size: 18px;
      font-weight: 700;
    }}
    .review-tools {{
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 12px;
      padding: 0 28px 18px;
    }}
    .tool-controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: flex-end;
    }}
    .tool-group {{
      display: grid;
      gap: 5px;
    }}
    .tool-label {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }}
    .tool-input, .tool-select {{
      min-height: 38px;
      min-width: 220px;
      padding: 0 10px;
      border: 1px solid var(--border);
      border-radius: 6px;
      background: #ffffff;
      color: var(--text);
      font: inherit;
    }}
    .tool-select {{
      min-width: 190px;
    }}
    .tool-input:focus, .tool-select:focus {{
      outline: 2px solid var(--focus);
      outline-offset: 1px;
    }}
    .export-button {{
      min-height: 38px;
      padding: 0 14px;
      border: 1px solid #1d4ed8;
      border-radius: 6px;
      background: var(--focus);
      color: #ffffff;
      font-weight: 700;
      cursor: pointer;
      white-space: nowrap;
    }}
    .export-button:hover {{
      background: #1d4ed8;
    }}
    main {{
      padding: 0 28px 32px;
    }}
    .table-wrap {{
      overflow-x: auto;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
    }}
    table {{
      width: 100%;
      min-width: 1760px;
      border-collapse: collapse;
    }}
    th, td {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--border);
      text-align: left;
      vertical-align: middle;
      white-space: nowrap;
    }}
    th {{
      background: #eef2f6;
      color: #334155;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    tr:last-child td {{
      border-bottom: 0;
    }}
    .filename {{
      max-width: 300px;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .keyframes {{
      display: flex;
      gap: 6px;
    }}
    .keyframes img {{
      display: block;
      width: 96px;
      height: 54px;
      object-fit: cover;
      background: #e5e7eb;
      border: 1px solid var(--border);
      border-radius: 6px;
    }}
    .badge {{
      display: inline-block;
      min-width: 42px;
      padding: 3px 8px;
      border-radius: 999px;
      font-weight: 700;
      text-align: center;
    }}
    .bad {{
      background: #fee4e2;
      color: var(--danger);
    }}
    .good {{
      background: #dcfae6;
      color: var(--ok);
    }}
    .warn {{
      background: #fef0c7;
      color: var(--warning);
    }}
    .empty {{
      color: var(--muted);
    }}
    .decision-buttons {{
      display: inline-grid;
      grid-template-columns: repeat(3, minmax(58px, 1fr));
      gap: 4px;
      width: 210px;
    }}
    .decision-button {{
      min-height: 30px;
      border: 1px solid var(--border);
      border-radius: 6px;
      background: #ffffff;
      color: var(--text);
      cursor: pointer;
      font-weight: 700;
    }}
    .decision-button:hover {{
      border-color: var(--focus);
    }}
    .decision-button.active[data-decision="keep"] {{
      background: #dcfae6;
      border-color: #75e0a7;
      color: var(--ok);
    }}
    .decision-button.active[data-decision="review"] {{
      background: #fef0c7;
      border-color: #fedf89;
      color: var(--warning);
    }}
    .decision-button.active[data-decision="reject"] {{
      background: #fee4e2;
      border-color: #fda29b;
      color: var(--danger);
    }}
    @media (max-width: 760px) {{
      .review-tools {{
        align-items: stretch;
        flex-direction: column;
      }}
      .tool-input, .tool-select {{
        min-width: 100%;
      }}
      .export-button {{
        width: 100%;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>{t["heading"]}</h1>
    <p class="summary">{t["summary"].format(count=count)}</p>
  </header>
  <section class="dashboard" aria-label="{t["dashboard_label"]}">
    <h2>{t["dashboard_label"]}</h2>
    <div class="dashboard-grid">
      {summary_cards}
    </div>
  </section>
  <section class="review-tools" aria-label="{t["review_tools"]}">
    <div class="tool-controls">
      <div class="tool-group">
        <label class="tool-label" for="video-search">{t["search"]}</label>
        <input class="tool-input" id="video-search" type="search" placeholder="{t["search_placeholder"]}">
      </div>
      <div class="tool-group">
        <label class="tool-label" for="recommendation-filter">{t["filter_recommendation"]}</label>
        <select class="tool-select" id="recommendation-filter">
          <option value="all">{t["all_recommendations"]}</option>
          <option value="keep">{t["keep"]}</option>
          <option value="review">{t["review"]}</option>
          <option value="reject_candidate">{t["reject_candidate"]}</option>
        </select>
      </div>
      <div class="tool-group">
        <label class="tool-label" for="priority-filter">{t["priority_review"]}</label>
        <select class="tool-select" id="priority-filter">
          <option value="all">{t["priority_all"]}</option>
          <option value="needs-review">{t["priority_needs_review"]}</option>
          <option value="likely-reject">{t["priority_likely_reject"]}</option>
          <option value="shaky-videos">{t["priority_shaky"]}</option>
          <option value="low-sharpness">{t["priority_low_sharpness"]}</option>
          <option value="exposure-problems">{t["priority_exposure"]}</option>
          <option value="long-videos">{t["priority_long"]}</option>
        </select>
      </div>
      <div class="tool-group">
        <label class="tool-label" for="sort-by">{t["sort_by"]}</label>
        <select class="tool-select" id="sort-by">
          <option value="default">{t["sort_default"]}</option>
          <option value="recommendation">{t["sort_recommendation"]}</option>
          <option value="duration-longest">{t["sort_duration_longest"]}</option>
          <option value="duration-shortest">{t["sort_duration_shortest"]}</option>
          <option value="blur-worst">{t["sort_blur_worst"]}</option>
          <option value="exposure-worst">{t["sort_exposure_worst"]}</option>
          <option value="stability-worst">{t["sort_stability_worst"]}</option>
          <option value="shaky-frames">{t["sort_shaky_frames"]}</option>
          <option value="keyframes">{t["sort_keyframes"]}</option>
        </select>
      </div>
    </div>
    <button class="export-button" id="export-video-decisions" type="button">{t["export_decisions"]}</button>
  </section>
  <main>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>{t["filename"]}</th>
            <th>{t["duration"]}</th>
            <th>{t["resolution"]}</th>
            <th>{t["fps"]}</th>
            <th>{t["codec"]}</th>
            <th>{t["keyframes"]}</th>
            <th>{t["avg_blur"]}</th>
            <th>{t["avg_exposure"]}</th>
            <th>{t["stability_score"]}</th>
            <th>{t["avg_motion"]}</th>
            <th>{t["max_motion"]}</th>
            <th>{t["shaky_frame_count"]}</th>
            <th>{t["stability_recommendation"]}</th>
            <th>{t["recommendation"]}</th>
            <th>{t["reason"]}</th>
            <th>{t["user_decision"]}</th>
          </tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
    </div>
  </main>
  <script>
    (() => {{
      const storageKey = "media_agent_video_user_decisions_v1";
      const rows = Array.from(document.querySelectorAll("tbody tr[data-file-path]"));
      const tbody = document.querySelector("tbody");
      const exportButton = document.getElementById("export-video-decisions");
      const searchInput = document.getElementById("video-search");
      const recommendationFilter = document.getElementById("recommendation-filter");
      const priorityFilter = document.getElementById("priority-filter");
      const sortSelect = document.getElementById("sort-by");
      const recommendationOrder = {{ "reject_candidate": 0, "review": 1, "keep": 2 }};
      const lowSharpnessThreshold = {LOW_SHARPNESS_THRESHOLD};
      const averageDuration = average(rows.map((row) => numberValue(row.dataset.durationSeconds)));

      function loadDecisions() {{
        try {{
          return JSON.parse(localStorage.getItem(storageKey) || "{{}}");
        }} catch (error) {{
          return {{}};
        }}
      }}

      function saveDecisions(decisions) {{
        try {{
          localStorage.setItem(storageKey, JSON.stringify(decisions));
        }} catch (error) {{
          return;
        }}
      }}

      function setActiveButton(row, decision) {{
        row.querySelectorAll(".decision-button").forEach((button) => {{
          button.classList.toggle("active", button.dataset.decision === decision);
        }});
      }}

      function csvCell(value) {{
        const text = String(value ?? "");
        if (/[",\\n\\r]/.test(text)) {{
          return `"${{text.replaceAll('"', '""')}}"`;
        }}
        return text;
      }}

      function exportDecisions(decisions) {{
        const header = ["file_path", "video_quality_recommendation", "user_decision"];
        const lines = [header.map(csvCell).join(",")];
        rows.forEach((row) => {{
          const filePath = row.dataset.filePath || "";
          const recommendation = row.dataset.videoQualityRecommendation || "";
          const userDecision = decisions[filePath] || "";
          lines.push([filePath, recommendation, userDecision].map(csvCell).join(","));
        }});

        const blob = new Blob([lines.join("\\n") + "\\n"], {{ type: "text/csv;charset=utf-8" }});
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "video_decisions.csv";
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
      }}

      function numberValue(value) {{
        const parsed = Number.parseFloat(value);
        return Number.isFinite(parsed) ? parsed : null;
      }}

      function average(values) {{
        const valid = values.filter((value) => value !== null);
        if (!valid.length) {{
          return null;
        }}
        return valid.reduce((sum, value) => sum + value, 0) / valid.length;
      }}

      function originalIndex(row) {{
        return Number.parseInt(row.dataset.originalIndex || "0", 10);
      }}

      function compareNumeric(a, b, datasetKey, direction = "asc") {{
        const aValue = numberValue(a.dataset[datasetKey]);
        const bValue = numberValue(b.dataset[datasetKey]);
        if (aValue === null && bValue === null) {{
          return originalIndex(a) - originalIndex(b);
        }}
        if (aValue === null) {{
          return 1;
        }}
        if (bValue === null) {{
          return -1;
        }}
        const comparison = aValue - bValue;
        return direction === "desc" ? -comparison : comparison;
      }}

      function compareRecommendation(a, b) {{
        const aValue = recommendationOrder[a.dataset.videoQualityRecommendation || ""] ?? 1;
        const bValue = recommendationOrder[b.dataset.videoQualityRecommendation || ""] ?? 1;
        if (aValue !== bValue) {{
          return aValue - bValue;
        }}
        return originalIndex(a) - originalIndex(b);
      }}

      function sortRows() {{
        const selectedSort = sortSelect.value || "default";
        const sortedRows = [...rows].sort((a, b) => {{
          let comparison = 0;
          if (selectedSort === "recommendation") {{
            comparison = compareRecommendation(a, b);
          }} else if (selectedSort === "duration-longest") {{
            comparison = compareNumeric(a, b, "durationSeconds", "desc");
          }} else if (selectedSort === "duration-shortest") {{
            comparison = compareNumeric(a, b, "durationSeconds", "asc");
          }} else if (selectedSort === "blur-worst") {{
            comparison = compareNumeric(a, b, "avgBlurScore", "asc");
          }} else if (selectedSort === "exposure-worst") {{
            comparison = compareNumeric(a, b, "avgExposureScore", "asc");
          }} else if (selectedSort === "stability-worst") {{
            comparison = compareNumeric(a, b, "stabilityScore", "asc");
          }} else if (selectedSort === "shaky-frames") {{
            comparison = compareNumeric(a, b, "shakyFrameCount", "desc");
          }} else if (selectedSort === "keyframes") {{
            comparison = compareNumeric(a, b, "frameCount", "desc");
          }} else {{
            comparison = originalIndex(a) - originalIndex(b);
          }}
          return comparison || originalIndex(a) - originalIndex(b);
        }});
        sortedRows.forEach((row) => tbody.appendChild(row));
      }}

      function matchesPriority(row, selectedPriority) {{
        const recommendation = row.dataset.videoQualityRecommendation || "";
        const stability = row.dataset.stabilityRecommendation || "";
        const duration = numberValue(row.dataset.durationSeconds);
        const overexposedCount = numberValue(row.dataset.overexposedFrameCount) || 0;
        const underexposedCount = numberValue(row.dataset.underexposedFrameCount) || 0;
        const blurScore = numberValue(row.dataset.avgBlurScore);
        if (selectedPriority === "needs-review") {{
          return recommendation === "review";
        }}
        if (selectedPriority === "likely-reject") {{
          return recommendation === "reject_candidate";
        }}
        if (selectedPriority === "shaky-videos") {{
          return stability === "shaky";
        }}
        if (selectedPriority === "low-sharpness") {{
          return row.dataset.lowSharpness === "true" || (blurScore !== null && blurScore < lowSharpnessThreshold);
        }}
        if (selectedPriority === "exposure-problems") {{
          return overexposedCount > 0 || underexposedCount > 0;
        }}
        if (selectedPriority === "long-videos") {{
          return averageDuration !== null && duration !== null && duration > averageDuration;
        }}
        return true;
      }}

      function applyFilters() {{
        const query = (searchInput.value || "").trim().toLowerCase();
        const selectedRecommendation = recommendationFilter.value || "all";
        const selectedPriority = priorityFilter.value || "all";
        rows.forEach((row) => {{
          const filename = (row.dataset.filename || "").toLowerCase();
          const recommendation = row.dataset.videoQualityRecommendation || "";
          const matchesSearch = !query || filename.includes(query);
          const matchesRecommendation = selectedRecommendation === "all" || recommendation === selectedRecommendation;
          const matchesPriorityFilter = matchesPriority(row, selectedPriority);
          row.hidden = !(matchesSearch && matchesRecommendation && matchesPriorityFilter);
        }});
      }}

      function updateReport() {{
        sortRows();
        applyFilters();
      }}

      const decisions = loadDecisions();
      rows.forEach((row) => {{
        const filePath = row.dataset.filePath || "";
        setActiveButton(row, decisions[filePath] || "");
        row.querySelectorAll(".decision-button").forEach((button) => {{
          button.addEventListener("click", () => {{
            decisions[filePath] = button.dataset.decision;
            saveDecisions(decisions);
            setActiveButton(row, decisions[filePath]);
          }});
        }});
      }});

      searchInput.addEventListener("input", updateReport);
      recommendationFilter.addEventListener("change", updateReport);
      priorityFilter.addEventListener("change", updateReport);
      sortSelect.addEventListener("change", updateReport);
      exportButton.addEventListener("click", () => exportDecisions(decisions));
      updateReport();
    }})();
  </script>
</body>
</html>
"""


def _render_dashboard_cards(dashboard: dict[str, Any], t: dict[str, str]) -> str:
    counts = dashboard["counts"]
    stability_counts = dashboard["stability_counts"]
    total = int(dashboard["total"])
    sections = [
        (
            None,
            [
                (t["total_videos"], total),
                (t["total_duration"], _format_duration(dashboard["total_duration"])),
                (t["average_duration"], _format_duration(dashboard["average_duration"])),
                (t["shortest_duration"], _format_duration(dashboard["shortest_duration"])),
                (t["longest_duration"], _format_duration(dashboard["longest_duration"])),
                (t["total_keyframes"], dashboard["total_keyframes"]),
                (t["average_keyframes"], _format_number(dashboard["average_keyframes"])),
                (t["generated_at"], dashboard["generated_at"]),
            ],
        ),
        (
            t["recommendation_distribution"],
            [
                (t["keep_count"], _format_count_percentage(counts.get("keep", 0), total)),
                (t["review_count"], _format_count_percentage(counts.get("review", 0), total)),
                (t["reject_count"], _format_count_percentage(counts.get("reject_candidate", 0), total)),
            ],
        ),
        (
            t["stability_distribution"],
            [
                (t["stable"], _format_count_percentage(stability_counts.get("stable", 0), total)),
                (t["moderate"], _format_count_percentage(stability_counts.get("moderate", 0), total)),
                (t["shaky"], _format_count_percentage(stability_counts.get("shaky", 0), total)),
            ],
        ),
        (
            t["technical_summary"],
            [
                (t["most_common_resolution"], dashboard["most_common_resolution"]),
                (t["most_common_fps"], dashboard["most_common_fps"]),
                (t["most_common_codec"], dashboard["most_common_codec"]),
            ],
        ),
        (
            t["quality_summary"],
            [
                (t["average_blur"], _format_number(dashboard["average_blur_score"])),
                (t["average_exposure"], _format_number(dashboard["average_exposure_score"])),
                (t["average_stability"], _format_number(dashboard["average_stability_score"])),
                (t["worst_blur_video"], dashboard["worst_blur_video"]),
                (t["worst_exposure_video"], dashboard["worst_exposure_video"]),
                (t["shakiest_video"], dashboard["shakiest_video"]),
            ],
        ),
    ]
    parts = []
    for title, cards in sections:
        if title:
            parts.append(f'<div class="dashboard-section-title">{escape(str(title))}</div>')
        for label, value in cards:
            parts.append(_render_dashboard_card(label, value))
    return "\n".join(parts)


def _render_dashboard_card(label: Any, value: Any) -> str:
    return (
        f"""<div class="dashboard-card"><span class="dashboard-label">{escape(str(label))}</span>"""
        f"""<span class="dashboard-value">{escape(str(value if value not in (None, "") else ""))}</span></div>"""
    )


def _data_attribute(value: Any) -> str:
    if value in (None, ""):
        return ""
    return escape(str(value), quote=True)


def _render_row(record: dict[str, Any], report_dir: Path, t: dict[str, str], original_index: int) -> str:
    recommendation = str(record.get("video_quality_recommendation") or "")
    badge_class = _badge_class(recommendation)
    width = record.get("width") or ""
    height = record.get("height") or ""
    resolution = f"{width} x {height}" if width and height else ""
    file_path = escape(str(record.get("file_path") or ""), quote=True)
    filename_value = escape(str(record.get("filename") or ""), quote=True)
    recommendation_value = escape(recommendation, quote=True)
    stability_value = escape(str(record.get("stability_recommendation") or ""), quote=True)
    low_sharpness = _number_or_default(record.get("avg_blur_score"), float("inf")) < LOW_SHARPNESS_THRESHOLD
    return f"""<tr data-file-path="{file_path}" data-filename="{filename_value}" data-video-quality-recommendation="{recommendation_value}" data-original-index="{original_index}" data-duration-seconds="{_data_attribute(record.get("duration_seconds"))}" data-avg-blur-score="{_data_attribute(record.get("avg_blur_score"))}" data-avg-exposure-score="{_data_attribute(record.get("avg_exposure_score"))}" data-stability-score="{_data_attribute(record.get("stability_score"))}" data-shaky-frame-count="{_data_attribute(record.get("shaky_frame_count"))}" data-frame-count="{_data_attribute(record.get("frame_count"))}" data-stability-recommendation="{stability_value}" data-overexposed-frame-count="{_data_attribute(record.get("overexposed_frame_count"))}" data-underexposed-frame-count="{_data_attribute(record.get("underexposed_frame_count"))}" data-low-sharpness="{str(low_sharpness).lower()}">
  <td class="filename" title="{escape(str(record.get("file_path") or ""))}">{escape(str(record.get("filename") or ""))}</td>
  <td>{escape(_format_duration(record.get("duration_seconds")))}</td>
  <td>{escape(resolution)}</td>
  <td>{escape(_format_number(record.get("fps")))}</td>
  <td>{escape(str(record.get("codec") or ""))}</td>
  <td>{_render_keyframes(record, report_dir, t)}</td>
  <td>{escape(_format_number(record.get("avg_blur_score")))}</td>
  <td>{escape(_format_number(record.get("avg_exposure_score")))}</td>
  <td>{escape(_format_number(record.get("stability_score")))}</td>
  <td>{escape(_format_number(record.get("avg_motion")))}</td>
  <td>{escape(_format_number(record.get("max_motion")))}</td>
  <td>{escape(str(record.get("shaky_frame_count") if record.get("shaky_frame_count") not in (None, "") else ""))}</td>
  <td>{escape(t.get(str(record.get("stability_recommendation") or ""), str(record.get("stability_recommendation") or "")))}</td>
  <td><span class="badge {badge_class}">{escape(t.get(recommendation, recommendation))}</span></td>
  <td>{escape(str(record.get("recommendation_reason") or ""))}</td>
  <td>{_render_decision_controls(t)}</td>
</tr>"""


def _render_keyframes(record: dict[str, Any], report_dir: Path, t: dict[str, str]) -> str:
    paths = [Path(path) for path in record.get("keyframe_paths") or []]
    preview_paths = paths[:3]
    if not preview_paths:
        return escape(t["no_keyframes"])
    images = []
    for path in preview_paths:
        src = os.path.relpath(path, report_dir)
        images.append(f'<img src="{escape(src)}" alt="{escape(path.name)}">')
    return f'<div class="keyframes">{"".join(images)}</div>'


def _badge_class(recommendation: str) -> str:
    if recommendation == "keep":
        return "good"
    if recommendation == "reject_candidate":
        return "bad"
    return "warn"


def _render_decision_controls(t: dict[str, str]) -> str:
    return f"""<div class="decision-buttons">
              <button class="decision-button" type="button" data-decision="keep">{t["keep"]}</button>
              <button class="decision-button" type="button" data-decision="review">{t["review"]}</button>
              <button class="decision-button" type="button" data-decision="reject">{t["reject"]}</button>
            </div>"""


def _format_count_percentage(count: Any, total: int) -> str:
    parsed_count = _int_or_default(count, 0)
    if total <= 0:
        return f"{parsed_count} (0%)"
    return f"{parsed_count} ({_format_percent(parsed_count / total * 100)})"


def _format_percent(value: float) -> str:
    return f"{value:.1f}%".replace(".0%", "%")


def _most_common(values: Any) -> str:
    cleaned = [str(value).strip() for value in values if str(value or "").strip()]
    if not cleaned:
        return ""
    return Counter(cleaned).most_common(1)[0][0]


def _resolution_value(record: dict[str, Any]) -> str:
    width = record.get("width")
    height = record.get("height")
    if width in (None, "") or height in (None, ""):
        return ""
    return f"{width} x {height}"


def _fps_value(record: dict[str, Any]) -> str:
    return _format_number(record.get("fps"))


def _filename_for_lowest(records: list[dict[str, Any]], field: str) -> str:
    candidates = []
    for record in records:
        value = _number_or_none(record.get(field))
        filename = str(record.get("filename") or "")
        if value is not None and filename:
            candidates.append((value, filename))
    if not candidates:
        return ""
    return min(candidates, key=lambda item: (item[0], item[1].lower()))[1]


def _average(values: Any) -> float | None:
    numbers = [_number_or_none(value) for value in values if value not in (None, "")]
    numbers = [number for number in numbers if number is not None]
    if not numbers:
        return None
    return sum(numbers) / len(numbers)


def _format_duration(value: Any) -> str:
    seconds = _number_or_none(value)
    if seconds is None:
        return ""
    minutes, remaining = divmod(int(round(seconds)), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{remaining:02d}"
    return f"{minutes:d}:{remaining:02d}"


def _format_number(value: Any) -> str:
    number = _number_or_none(value)
    if number is None:
        return ""
    return f"{number:.2f}".rstrip("0").rstrip(".")


def _number_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _number_or_default(value: Any, default: float) -> float:
    parsed = _number_or_none(value)
    return parsed if parsed is not None else default


def _int_or_default(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

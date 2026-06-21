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

TRANSLATIONS = {
    "zh": {
        "html_lang": "zh-CN",
        "title": "Media Agent 报告",
        "heading": "Media Agent 报告",
        "summary": "共 {count} 个素材，已按保留建议和重复组排序。",
        "topbar_label": "推荐统计和导出",
        "recommended_keep": "推荐保留数量",
        "recommended_review": "推荐复查数量",
        "recommended_reject": "删除候选数量",
        "dashboard_label": "项目统计摘要",
        "total_images": "总图片数量",
        "duplicate_groups": "重复组数量",
        "best_picks": "组内最佳数量",
        "waste_candidates": "废片候选数量",
        "memory_safe_overrides": "回忆保护覆盖数量",
        "high_memory_risk": "高回忆风险数量",
        "technical_rejects": "技术删除候选数量",
        "final_rejects": "最终删除候选数量",
        "average_blur": "平均清晰度",
        "average_exposure": "平均曝光",
        "ai_providers": "AI来源",
        "generated_at": "报告生成时间",
        "export_decisions": "导出人工选择结果",
        "thumbnail": "缩略图",
        "filename": "文件名",
        "taken_at": "拍摄时间",
        "camera_model": "相机型号",
        "dimensions": "尺寸",
        "exposure": "曝光评分",
        "blur": "清晰度评分",
        "waste": "废片候选",
        "duplicate_group_id": "重复组",
        "duplicate_count": "重复数量",
        "is_duplicate_candidate": "重复候选",
        "group_best_pick": "组内最佳",
        "group_rank": "组内排名",
        "technical_recommendation": "技术建议",
        "final_recommendation": "最终建议",
        "keep_recommendation": "系统建议",
        "recommendation_reason": "推荐原因",
        "memory_risk": "回忆风险",
        "memory_risk_reason": "回忆风险原因",
        "content_safety_override": "内容保护覆盖",
        "ai_description": "AI描述",
        "ai_tags": "AI标签",
        "scene_type": "场景类型",
        "subject_type": "主体类型",
        "suggested_use": "建议用途",
        "ai_confidence": "AI置信度",
        "ai_provider": "AI来源",
        "user_decision": "人工决定",
        "no_thumbnail": "无",
        "keep": "保留",
        "review": "复查",
        "reject": "剔除",
        "reject_candidate": "删除候选",
        "memory_safe_review": "回忆保护复查",
    },
    "en": {
        "html_lang": "en",
        "title": "Media Agent Report",
        "heading": "Media Agent Report",
        "summary": "{count} media files, sorted by recommendation and duplicate group.",
        "topbar_label": "Recommendation stats and export",
        "recommended_keep": "Recommended Keep",
        "recommended_review": "Recommended Review",
        "recommended_reject": "Reject Candidates",
        "dashboard_label": "Project Summary Dashboard",
        "total_images": "Total Images",
        "duplicate_groups": "Duplicate Groups",
        "best_picks": "Best Picks",
        "waste_candidates": "Waste Candidates",
        "memory_safe_overrides": "Memory-Safe Override Count",
        "high_memory_risk": "High Memory Risk Count",
        "technical_rejects": "Technical Reject Count",
        "final_rejects": "Final Reject Count",
        "average_blur": "Average Blur Score",
        "average_exposure": "Average Exposure Score",
        "ai_providers": "AI Provider",
        "generated_at": "Report Generated At",
        "export_decisions": "Export Decisions",
        "thumbnail": "Thumbnail",
        "filename": "Filename",
        "taken_at": "Taken At",
        "camera_model": "Camera Model",
        "dimensions": "Dimensions",
        "exposure": "Exposure Score",
        "blur": "Blur Score",
        "waste": "Waste Candidate",
        "duplicate_group_id": "Duplicate Group",
        "duplicate_count": "Duplicate Count",
        "is_duplicate_candidate": "Duplicate Candidate",
        "group_best_pick": "Best Pick",
        "group_rank": "Group Rank",
        "technical_recommendation": "Technical Recommendation",
        "final_recommendation": "Final Recommendation",
        "keep_recommendation": "Recommendation",
        "recommendation_reason": "Recommendation Reason",
        "memory_risk": "Memory Risk",
        "memory_risk_reason": "Memory Risk Reason",
        "content_safety_override": "Content Safety Override",
        "ai_description": "AI Description",
        "ai_tags": "AI Tags",
        "scene_type": "Scene Type",
        "subject_type": "Subject Type",
        "suggested_use": "Suggested Use",
        "ai_confidence": "AI Confidence",
        "ai_provider": "AI Provider",
        "user_decision": "User Decision",
        "no_thumbnail": "None",
        "keep": "keep",
        "review": "review",
        "reject": "reject",
        "reject_candidate": "reject_candidate",
        "memory_safe_review": "memory-safe review",
    },
}


def sort_records_for_review(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    group_priorities = _group_recommendation_priorities(records)
    return sorted(records, key=lambda record: _review_sort_key(record, group_priorities))


def export_html_report(records: list[dict[str, Any]], output_path: Path, language: str = "zh") -> None:
    t = _translations(language)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = "\n".join(_render_row(record, output_path.parent, t) for record in records)
    dashboard = _build_dashboard(records)
    output_path.write_text(_render_page(rows, len(records), dashboard, t), encoding="utf-8")


def _translations(language: str) -> dict[str, str]:
    return TRANSLATIONS.get(language, TRANSLATIONS["zh"])


def _group_recommendation_priorities(records: list[dict[str, Any]]) -> dict[str, int]:
    priorities: dict[str, int] = {}
    for record in records:
        group_key = _group_sort_key(record)
        recommendation_rank = _recommendation_rank(record.get("keep_recommendation"))
        priorities[group_key] = min(priorities.get(group_key, recommendation_rank), recommendation_rank)
    return priorities


def _review_sort_key(record: dict[str, Any], group_priorities: dict[str, int]) -> tuple[int, str, int, int, float, str]:
    group_key = _group_sort_key(record)
    group_priority = group_priorities.get(group_key, _recommendation_rank(record.get("keep_recommendation")))
    group_rank = _int_or_default(record.get("group_rank"), 9999)
    recommendation_rank = _recommendation_rank(record.get("keep_recommendation"))
    blur_score = _number_or_default(record.get("blur_score"), float("inf"))
    filename = str(record.get("filename") or "").lower()
    return (group_priority, group_key, group_rank, recommendation_rank, blur_score, filename)


def _recommendation_counts(records: list[dict[str, Any]]) -> Counter[str]:
    return Counter(str(record.get("keep_recommendation") or "") for record in records)


def _average(values: Any) -> float | None:
    numbers = [_number_or_default(value, None) for value in values if value not in (None, "")]
    numbers = [number for number in numbers if number is not None]
    if not numbers:
        return None
    return sum(numbers) / len(numbers)


def _build_dashboard(records: list[dict[str, Any]]) -> dict[str, Any]:
    counts = _recommendation_counts(records)
    total = len(records)
    duplicate_groups = {str(record.get("duplicate_group_id")) for record in records if record.get("duplicate_group_id")}
    ai_providers = sorted({str(record.get("ai_provider")) for record in records if record.get("ai_provider")})
    return {
        "total": total,
        "counts": counts,
        "duplicate_group_count": len(duplicate_groups),
        "best_pick_count": sum(1 for record in records if record.get("group_best_pick") is True),
        "waste_candidate_count": sum(1 for record in records if record.get("waste_candidate") is True),
        "memory_safe_override_count": sum(1 for record in records if record.get("content_safety_override") is True),
        "high_memory_risk_count": sum(1 for record in records if record.get("memory_risk") == "high"),
        "technical_reject_count": sum(1 for record in records if record.get("technical_recommendation") == "reject_candidate"),
        "final_reject_count": sum(1 for record in records if record.get("final_recommendation") == "reject_candidate"),
        "average_blur_score": _average(record.get("blur_score") for record in records),
        "average_exposure_score": _average(record.get("exposure_score") for record in records),
        "ai_provider": ", ".join(ai_providers) if ai_providers else "none",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


def _render_page(rows: str, count: int, dashboard: dict[str, Any], t: dict[str, str]) -> str:
    counts = dashboard["counts"]
    keep_count = counts.get("keep", 0)
    review_count = counts.get("review", 0)
    reject_count = counts.get("reject_candidate", 0)
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
    .topbar {{
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 16px;
      padding: 0 28px 18px;
    }}
    .stats {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .stat {{
      min-width: 120px;
      padding: 10px 12px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 8px;
    }}
    .stat-label {{
      display: block;
      color: var(--muted);
      font-size: 12px;
    }}
    .stat-value {{
      display: block;
      margin-top: 3px;
      font-size: 20px;
      font-weight: 700;
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
    }}
    .export-button:hover {{
      background: #1d4ed8;
    }}
    .dashboard {{
      padding: 0 28px 18px;
    }}
    .dashboard-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
      gap: 10px;
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
      border-collapse: collapse;
      min-width: 3100px;
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
    img {{
      display: block;
      width: 96px;
      height: 72px;
      object-fit: cover;
      background: #e5e7eb;
      border: 1px solid var(--border);
      border-radius: 6px;
    }}
    .filename {{
      max-width: 280px;
      overflow: hidden;
      text-overflow: ellipsis;
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
  </style>
</head>
<body>
  <header>
    <h1>{t["heading"]}</h1>
    <p class="summary">{t["summary"].format(count=count)}</p>
  </header>
  <section class="topbar" aria-label="{t["topbar_label"]}">
    <div class="stats">
      <div class="stat">
        <span class="stat-label">{t["recommended_keep"]}</span>
        <span class="stat-value">{keep_count}</span>
      </div>
      <div class="stat">
        <span class="stat-label">{t["recommended_review"]}</span>
        <span class="stat-value">{review_count}</span>
      </div>
      <div class="stat">
        <span class="stat-label">{t["recommended_reject"]}</span>
        <span class="stat-value">{reject_count}</span>
      </div>
    </div>
    <button class="export-button" id="export-decisions" type="button">{t["export_decisions"]}</button>
  </section>
  <section class="dashboard" aria-label="{t["dashboard_label"]}">
    <div class="dashboard-grid">
{summary_cards}
    </div>
  </section>
  <main>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>{t["thumbnail"]}</th>
            <th>{t["filename"]}</th>
            <th>{t["taken_at"]}</th>
            <th>{t["camera_model"]}</th>
            <th>{t["dimensions"]}</th>
            <th>{t["exposure"]}</th>
            <th>{t["blur"]}</th>
            <th>{t["waste"]}</th>
            <th>{t["duplicate_group_id"]}</th>
            <th>{t["duplicate_count"]}</th>
            <th>{t["is_duplicate_candidate"]}</th>
            <th>{t["group_best_pick"]}</th>
            <th>{t["group_rank"]}</th>
            <th>{t["technical_recommendation"]}</th>
            <th>{t["final_recommendation"]}</th>
            <th>{t["keep_recommendation"]}</th>
            <th>{t["recommendation_reason"]}</th>
            <th>{t["memory_risk"]}</th>
            <th>{t["memory_risk_reason"]}</th>
            <th>{t["content_safety_override"]}</th>
            <th>{t["ai_description"]}</th>
            <th>{t["ai_tags"]}</th>
            <th>{t["scene_type"]}</th>
            <th>{t["subject_type"]}</th>
            <th>{t["suggested_use"]}</th>
            <th>{t["ai_confidence"]}</th>
            <th>{t["ai_provider"]}</th>
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
      const storageKey = "media_agent_user_decisions_v1";
      const rows = Array.from(document.querySelectorAll("tbody tr[data-file-path]"));
      const exportButton = document.getElementById("export-decisions");

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
        const header = ["file_path", "keep_recommendation", "user_decision"];
        const lines = [header.map(csvCell).join(",")];
        rows.forEach((row) => {{
          const filePath = row.dataset.filePath || "";
          const recommendation = row.dataset.keepRecommendation || "";
          const userDecision = decisions[filePath] || "";
          lines.push([filePath, recommendation, userDecision].map(csvCell).join(","));
        }});

        const blob = new Blob([lines.join("\\n") + "\\n"], {{ type: "text/csv;charset=utf-8" }});
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "decisions.csv";
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
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

      exportButton.addEventListener("click", () => exportDecisions(decisions));
    }})();
  </script>
</body>
</html>
"""


def _render_dashboard_cards(dashboard: dict[str, Any], t: dict[str, str]) -> str:
    total = int(dashboard["total"])
    counts = dashboard["counts"]
    cards = [
        (t["total_images"], str(total)),
        (t["recommended_keep"], _count_with_percent(counts.get("keep", 0), total)),
        (t["recommended_review"], _count_with_percent(counts.get("review", 0), total)),
        (t["recommended_reject"], _count_with_percent(counts.get("reject_candidate", 0), total)),
        (t["duplicate_groups"], str(dashboard["duplicate_group_count"])),
        (t["best_picks"], str(dashboard["best_pick_count"])),
        (t["waste_candidates"], str(dashboard["waste_candidate_count"])),
        (t["memory_safe_overrides"], str(dashboard["memory_safe_override_count"])),
        (t["high_memory_risk"], str(dashboard["high_memory_risk_count"])),
        (t["technical_rejects"], str(dashboard["technical_reject_count"])),
        (t["final_rejects"], str(dashboard["final_reject_count"])),
        (t["average_blur"], _format_number(dashboard["average_blur_score"])),
        (t["average_exposure"], _format_number(dashboard["average_exposure_score"])),
        (t["ai_providers"], escape(str(dashboard["ai_provider"]))),
        (t["generated_at"], escape(str(dashboard["generated_at"]))),
    ]
    return "\n".join(
        f"""      <div class="dashboard-card">
        <span class="dashboard-label">{label}</span>
        <span class="dashboard-value">{value}</span>
      </div>"""
        for label, value in cards
    )


def _count_with_percent(count: int, total: int) -> str:
    if total <= 0:
        return f"{count} (0.0%)"
    return f"{count} ({count / total * 100:.1f}%)"


def _format_number(value: Any) -> str:
    if value is None:
        return "-"
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return "-"


def _render_row(record: dict[str, Any], report_dir: Path, t: dict[str, str]) -> str:
    thumbnail = _render_thumbnail(record.get("thumbnail_path"), report_dir, t)
    filename = escape(str(record.get("filename") or ""))
    taken_at = _cell(record.get("taken_at"))
    camera_model = _cell(record.get("camera_model"))
    dimensions = _dimensions(record)
    exposure_score = _cell(record.get("exposure_score"))
    blur_score = _cell(record.get("blur_score"))
    waste_candidate = _render_bool_bad(record.get("waste_candidate"))
    duplicate_group_id = _cell(record.get("duplicate_group_id"))
    duplicate_count = _cell(record.get("duplicate_count"))
    is_duplicate_candidate = _render_bool_bad(record.get("is_duplicate_candidate"))
    group_best_pick = _render_bool_good(record.get("group_best_pick"))
    group_rank = _cell(record.get("group_rank"))
    technical_recommendation = _render_recommendation(record.get("technical_recommendation"), t)
    final_recommendation = _render_recommendation(record.get("final_recommendation"), t)
    keep_recommendation = _render_recommendation(record.get("keep_recommendation"), t)
    recommendation_reason = _cell(record.get("recommendation_reason"))
    memory_risk = _cell(record.get("memory_risk"))
    memory_risk_reason = _cell(record.get("memory_risk_reason"))
    content_safety_override = _render_content_safety_override(record.get("content_safety_override"), t)
    ai_description = _ai_cell(record.get("ai_description"))
    ai_tags = _ai_cell(record.get("ai_tags"))
    scene_type = _ai_cell(record.get("scene_type"))
    subject_type = _ai_cell(record.get("subject_type"))
    suggested_use = _ai_cell(record.get("suggested_use"))
    ai_confidence = _ai_cell(record.get("ai_confidence"))
    ai_provider = _ai_cell(record.get("ai_provider"))
    file_path = escape(str(record.get("path") or ""), quote=True)
    keep_recommendation_value = escape(str(record.get("keep_recommendation") or ""), quote=True)

    return f"""          <tr data-file-path="{file_path}" data-keep-recommendation="{keep_recommendation_value}">
            <td>{thumbnail}</td>
            <td class="filename" title="{filename}">{filename}</td>
            <td>{taken_at}</td>
            <td>{camera_model}</td>
            <td>{dimensions}</td>
            <td>{exposure_score}</td>
            <td>{blur_score}</td>
            <td>{waste_candidate}</td>
            <td>{duplicate_group_id}</td>
            <td>{duplicate_count}</td>
            <td>{is_duplicate_candidate}</td>
            <td>{group_best_pick}</td>
            <td>{group_rank}</td>
            <td>{technical_recommendation}</td>
            <td>{final_recommendation}</td>
            <td>{keep_recommendation}</td>
            <td>{recommendation_reason}</td>
            <td>{memory_risk}</td>
            <td>{memory_risk_reason}</td>
            <td>{content_safety_override}</td>
            <td>{ai_description}</td>
            <td>{ai_tags}</td>
            <td>{scene_type}</td>
            <td>{subject_type}</td>
            <td>{suggested_use}</td>
            <td>{ai_confidence}</td>
            <td>{ai_provider}</td>
            <td>{_render_decision_controls(t)}</td>
          </tr>"""


def _render_thumbnail(thumbnail_path: Any, report_dir: Path, t: dict[str, str]) -> str:
    if not thumbnail_path:
        return f'<span class="empty">{t["no_thumbnail"]}</span>'
    path = Path(str(thumbnail_path))
    src = _relative_path(path, report_dir)
    escaped_src = escape(str(src))
    return f'<img src="{escaped_src}" alt="">'


def _relative_path(path: Path, start: Path) -> str:
    return os.path.relpath(path.resolve(), start.resolve())


def _dimensions(record: dict[str, Any]) -> str:
    width = record.get("width")
    height = record.get("height")
    if width in (None, "") or height in (None, ""):
        return '<span class="empty">-</span>'
    return f"{escape(str(width))} x {escape(str(height))}"


def _render_bool_bad(value: Any) -> str:
    if value is True:
        return '<span class="badge bad">True</span>'
    if value is False:
        return '<span class="badge good">False</span>'
    return '<span class="empty">-</span>'


def _render_bool_good(value: Any) -> str:
    if value is True:
        return '<span class="badge good">True</span>'
    if value is False:
        return '<span class="badge">False</span>'
    return '<span class="empty">-</span>'


def _render_content_safety_override(value: Any, t: dict[str, str]) -> str:
    if value is True:
        return f'<span class="badge warn">{t["memory_safe_review"]}</span>'
    if value is False:
        return '<span class="badge">False</span>'
    return '<span class="empty">-</span>'


def _render_recommendation(value: Any, t: dict[str, str]) -> str:
    if value == "reject_candidate":
        return f'<span class="badge bad">{t["reject_candidate"]}</span>'
    if value == "review":
        return f'<span class="badge warn">{t["review"]}</span>'
    if value == "keep":
        return f'<span class="badge good">{t["keep"]}</span>'
    return '<span class="empty">-</span>'


def _render_decision_controls(t: dict[str, str]) -> str:
    return f"""<div class="decision-buttons">
              <button class="decision-button" type="button" data-decision="keep">{t["keep"]}</button>
              <button class="decision-button" type="button" data-decision="review">{t["review"]}</button>
              <button class="decision-button" type="button" data-decision="reject">{t["reject"]}</button>
            </div>"""


def _cell(value: Any) -> str:
    if value in (None, ""):
        return '<span class="empty">-</span>'
    return escape(str(value))


def _ai_cell(value: Any) -> str:
    if value in (None, ""):
        return ""
    return escape(str(value))


def _group_sort_key(record: dict[str, Any]) -> str:
    group_id = record.get("duplicate_group_id")
    if group_id:
        return f"group:{group_id}"
    return f"single:{str(record.get('filename') or '').lower()}"


def _recommendation_rank(value: Any) -> int:
    return RECOMMENDATION_ORDER.get(str(value), RECOMMENDATION_ORDER["review"])


def _number_or_default(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int_or_default(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

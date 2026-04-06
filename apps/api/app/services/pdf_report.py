"""PDF report generation service using WeasyPrint + Jinja2."""

import io
from datetime import datetime
from jinja2 import Environment, BaseLoader

from weasyprint import HTML


REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {
    size: A4;
    margin: 2cm;
    @bottom-center { content: "Page " counter(page) " of " counter(pages); font-size: 9px; color: #888; }
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Helvetica Neue', Arial, sans-serif; color: #1a1a2e; font-size: 11px; line-height: 1.5; }

  /* Header */
  .header { background: linear-gradient(135deg, #0d9488, #0f766e); color: white; padding: 30px; margin: -2cm -2cm 20px -2cm; padding: 30px 2cm; }
  .header h1 { font-size: 24px; font-weight: 700; margin-bottom: 4px; }
  .header .subtitle { font-size: 12px; opacity: 0.85; }
  .header .period { font-size: 10px; opacity: 0.7; margin-top: 8px; }

  /* Section */
  .section { margin-bottom: 24px; page-break-inside: avoid; }
  .section-title { font-size: 14px; font-weight: 700; color: #0d9488; border-bottom: 2px solid #0d9488; padding-bottom: 4px; margin-bottom: 12px; }

  /* Executive Summary */
  .exec-summary { background: #f0fdfa; border-left: 4px solid #0d9488; padding: 16px; border-radius: 0 8px 8px 0; font-size: 12px; line-height: 1.6; }

  /* KPI Table */
  table { width: 100%; border-collapse: collapse; margin-bottom: 12px; }
  th { background: #f1f5f9; color: #475569; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; padding: 8px 10px; text-align: left; border-bottom: 2px solid #e2e8f0; }
  td { padding: 8px 10px; border-bottom: 1px solid #e2e8f0; font-size: 11px; }
  tr:nth-child(even) { background: #f8fafc; }
  .delta-positive { color: #059669; font-weight: 600; }
  .delta-negative { color: #dc2626; font-weight: 600; }

  /* Alerts */
  .alert-card { border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px 14px; margin-bottom: 8px; }
  .alert-high { border-left: 4px solid #dc2626; }
  .alert-medium { border-left: 4px solid #f59e0b; }
  .alert-low { border-left: 4px solid #3b82f6; }
  .alert-title { font-weight: 600; font-size: 11px; }
  .alert-desc { font-size: 10px; color: #64748b; margin-top: 2px; }
  .alert-badge { display: inline-block; font-size: 8px; font-weight: 700; text-transform: uppercase; padding: 2px 6px; border-radius: 3px; margin-left: 6px; }
  .badge-high { background: #fef2f2; color: #dc2626; }
  .badge-medium { background: #fffbeb; color: #d97706; }
  .badge-low { background: #eff6ff; color: #3b82f6; }

  /* SOV */
  .sov-bar-container { display: flex; align-items: center; margin-bottom: 6px; }
  .sov-label { width: 140px; font-size: 10px; font-weight: 500; }
  .sov-bar-bg { flex: 1; height: 18px; background: #e2e8f0; border-radius: 4px; overflow: hidden; }
  .sov-bar { height: 100%; background: linear-gradient(90deg, #0d9488, #14b8a6); border-radius: 4px; }
  .sov-pct { width: 50px; text-align: right; font-size: 10px; font-weight: 600; color: #0d9488; }

  /* Themes */
  .theme-chip { display: inline-block; background: #f0fdfa; border: 1px solid #99f6e4; color: #0f766e; padding: 4px 10px; border-radius: 12px; font-size: 10px; margin: 3px 4px 3px 0; }

  /* Takeaways */
  .takeaway { padding: 8px 0; border-bottom: 1px dashed #e2e8f0; font-size: 11px; }
  .takeaway:last-child { border-bottom: none; }
  .takeaway-num { display: inline-block; width: 20px; height: 20px; background: #0d9488; color: white; border-radius: 50%; text-align: center; line-height: 20px; font-size: 9px; font-weight: 700; margin-right: 8px; }

  /* Opportunities */
  .opp-card { background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 12px; margin-bottom: 8px; }
  .opp-title { font-weight: 600; font-size: 11px; color: #166534; }
  .opp-desc { font-size: 10px; color: #475569; margin-top: 4px; }

  /* Competitors table */
  .tier-badge { display: inline-block; font-size: 8px; font-weight: 700; text-transform: uppercase; padding: 2px 6px; border-radius: 3px; }
  .tier-direct { background: #fef2f2; color: #dc2626; }
  .tier-indirect { background: #fffbeb; color: #d97706; }
  .tier-aspirational { background: #eff6ff; color: #3b82f6; }

  /* Footer */
  .footer { margin-top: 30px; padding-top: 12px; border-top: 1px solid #e2e8f0; font-size: 9px; color: #94a3b8; text-align: center; }
</style>
</head>
<body>

<!-- Header -->
<div class="header">
  <h1>Competitive Intelligence Report</h1>
  <div class="subtitle">{{ brand_name }}</div>
  <div class="period">{{ filter_mode | capitalize }} Report &mdash; {{ period_start }} to {{ period_end }}</div>
</div>

<!-- Executive Summary -->
{% if executive_summary %}
<div class="section">
  <div class="section-title">Executive Summary</div>
  <div class="exec-summary">{{ executive_summary }}</div>
</div>
{% endif %}

<!-- Key Takeaways -->
{% if key_takeaways %}
<div class="section">
  <div class="section-title">Key Takeaways</div>
  {% for t in key_takeaways %}
  <div class="takeaway"><span class="takeaway-num">{{ loop.index }}</span>{{ t }}</div>
  {% endfor %}
</div>
{% endif %}

<!-- Competitors Analyzed -->
{% if competitors %}
<div class="section">
  <div class="section-title">Competitors Analyzed</div>
  <table>
    <thead><tr><th>Competitor</th><th>Tier</th></tr></thead>
    <tbody>
    {% for c in competitors %}
    <tr>
      <td>{{ c.name }}</td>
      <td><span class="tier-badge tier-{{ c.tier }}">{{ c.tier }}</span></td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
</div>
{% endif %}

<!-- KPI Summary -->
{% if kpi_rows %}
<div class="section">
  <div class="section-title">KPI Summary</div>
  <table>
    <thead><tr><th>Competitor</th><th>KPI</th><th>Value</th><th>Change</th></tr></thead>
    <tbody>
    {% for row in kpi_rows %}
    <tr>
      <td>{{ row.competitor }}</td>
      <td>{{ row.label }}</td>
      <td>{{ row.value }}</td>
      <td>
        {% if row.delta is not none %}
          <span class="{{ 'delta-positive' if row.delta > 0 else 'delta-negative' }}">
            {{ '+' if row.delta > 0 else '' }}{{ '%.1f' | format(row.delta) }}%
          </span>
        {% else %}
          &mdash;
        {% endif %}
      </td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
</div>
{% endif %}

<!-- Share of Voice -->
{% if sov_entries %}
<div class="section">
  <div class="section-title">Share of Voice</div>
  {% for e in sov_entries %}
  <div class="sov-bar-container">
    <div class="sov-label">{{ e.brand_name }}</div>
    <div class="sov-bar-bg"><div class="sov-bar" style="width: {{ e.sov_pct }}%"></div></div>
    <div class="sov-pct">{{ e.sov_pct }}%</div>
  </div>
  {% endfor %}
</div>
{% endif %}

<!-- Messaging Themes -->
{% if themes %}
<div class="section">
  <div class="section-title">Messaging Landscape</div>
  <div>
  {% for t in themes %}
    <span class="theme-chip">{{ t.theme }} ({{ t.frequency }}x)</span>
  {% endfor %}
  </div>
</div>
{% endif %}

<!-- Alerts -->
{% if alerts %}
<div class="section">
  <div class="section-title">Alerts</div>
  {% for a in alerts %}
  <div class="alert-card alert-{{ a.severity }}">
    <div class="alert-title">
      {{ a.title }}
      <span class="alert-badge badge-{{ a.severity }}">{{ a.severity }}</span>
    </div>
    <div class="alert-desc">{{ a.description }}</div>
  </div>
  {% endfor %}
</div>
{% endif %}

<!-- Opportunities -->
{% if opportunities %}
<div class="section">
  <div class="section-title">Opportunities</div>
  {% for o in opportunities %}
  <div class="opp-card">
    <div class="opp-title">{{ o.title }}</div>
    <div class="opp-desc">{{ o.description }}</div>
  </div>
  {% endfor %}
</div>
{% endif %}

<!-- Footer -->
<div class="footer">
  Generated by CompeteIQ on {{ generated_at }} &bull; Confidential
</div>

</body>
</html>
"""


def _build_kpi_rows(kpi_summary: dict, competitors: list[dict]) -> list[dict]:
    """Flatten KPI summary dict into table rows."""
    comp_lookup = {c["id"]: c["name"] for c in competitors}
    rows = []
    for comp_key, kpis in kpi_summary.items():
        comp_name = comp_lookup.get(comp_key, "Benchmark" if comp_key == "benchmark" else comp_key[:8])
        for kpi_key, data in kpis.items():
            if kpi_key.endswith("_benchmark"):
                continue
            rows.append({
                "competitor": comp_name,
                "label": data.get("label", kpi_key.replace("_", " ").title()),
                "value": f"{data.get('value', 0):,.2f}",
                "delta": data.get("delta_pct"),
            })
    return rows


def generate_pdf(report_data: dict, brand_name: str) -> bytes:
    """Generate a PDF from report data. Returns raw PDF bytes."""
    env = Environment(loader=BaseLoader())
    template = env.from_string(REPORT_TEMPLATE)

    period = report_data.get("period", {})
    competitors = report_data.get("competitors_analyzed", [])

    context = {
        "brand_name": brand_name,
        "filter_mode": period.get("filter_mode", "weekly"),
        "period_start": period.get("start", ""),
        "period_end": period.get("end", ""),
        "executive_summary": report_data.get("executive_summary", ""),
        "key_takeaways": report_data.get("key_takeaways", []),
        "competitors": competitors,
        "kpi_rows": _build_kpi_rows(report_data.get("kpi_summary", {}), competitors),
        "sov_entries": sorted(
            report_data.get("share_of_voice", []),
            key=lambda e: e.get("sov_pct", 0),
            reverse=True,
        ),
        "themes": report_data.get("messaging_landscape", []),
        "alerts": report_data.get("alerts", []),
        "opportunities": report_data.get("opportunities", []),
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    }

    html_str = template.render(**context)
    pdf_bytes = HTML(string=html_str).write_pdf()
    return pdf_bytes

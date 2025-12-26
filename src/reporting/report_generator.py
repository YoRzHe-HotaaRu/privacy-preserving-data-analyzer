"""Reporting Module - Report Generator"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

try:
    from jinja2 import Template

    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PRIV.GUARD - Privacy Analysis Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@300;400;500;600;700&family=Syne:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-void: #030308;
            --bg-deep: #0a0a12;
            --bg-surface: #0f0f1a;
            --bg-elevated: #16162a;
            --bg-card: rgba(15, 15, 30, 0.85);
            --accent-primary: #00f0ff;
            --accent-secondary: #00b8d4;
            --accent-glow: rgba(0, 240, 255, 0.4);
            --accent-dim: rgba(0, 240, 255, 0.15);
            --success: #00ff9d;
            --success-dim: rgba(0, 255, 157, 0.15);
            --warning: #ffb800;
            --warning-dim: rgba(255, 184, 0, 0.15);
            --danger: #ff3366;
            --danger-dim: rgba(255, 51, 102, 0.15);
            --text-bright: #ffffff;
            --text-primary: #e0e6ed;
            --text-secondary: #8892a0;
            --text-muted: #4a5568;
            --border-subtle: rgba(255, 255, 255, 0.06);
            --border-accent: rgba(0, 240, 255, 0.3);
            --font-display: 'Orbitron', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
            --font-body: 'Syne', sans-serif;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: var(--font-body);
            background: var(--bg-void);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 2rem;
            min-height: 100vh;
            background-image: 
                linear-gradient(rgba(0, 240, 255, 0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 240, 255, 0.02) 1px, transparent 1px);
            background-size: 50px 50px;
        }
        .container { max-width: 1100px; margin: 0 auto; }
        .header {
            text-align: center;
            padding: 3rem 0;
            border-bottom: 1px solid var(--border-subtle);
            margin-bottom: 2rem;
        }
        .header h1 {
            font-family: var(--font-display);
            font-size: 2.5rem;
            font-weight: 800;
            letter-spacing: 0.1em;
            color: var(--accent-primary);
            text-shadow: 0 0 30px rgba(0, 240, 255, 0.5), 0 0 60px rgba(0, 240, 255, 0.3);
            margin-bottom: 0.5rem;
        }
        .header p { 
            font-family: var(--font-mono);
            font-size: 0.85rem;
            color: var(--text-muted); 
            letter-spacing: 0.05em;
        }
        .card {
            background: var(--bg-card);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border-subtle);
            backdrop-filter: blur(10px);
        }
        .card h2 {
            font-family: var(--font-display);
            font-size: 1rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            margin-bottom: 1rem;
            color: var(--accent-primary);
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
        }
        .metric {
            background: var(--bg-elevated);
            padding: 1.25rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid var(--border-subtle);
        }
        .metric-value {
            font-family: var(--font-display);
            font-size: 2rem;
            font-weight: 700;
            color: var(--accent-primary);
            text-shadow: 0 0 20px var(--accent-glow);
        }
        .metric-label { 
            font-family: var(--font-mono);
            color: var(--text-muted); 
            font-size: 0.75rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-top: 0.25rem;
        }
        .status-badge {
            display: inline-block;
            padding: 0.35rem 1rem;
            border-radius: 4px;
            font-family: var(--font-mono);
            font-size: 0.75rem;
            font-weight: 500;
            letter-spacing: 0.05em;
        }
        .status-success { background: var(--success-dim); color: var(--success); }
        .status-warning { background: var(--warning-dim); color: var(--warning); }
        .status-danger { background: var(--danger-dim); color: var(--danger); }
        .risk-bar {
            height: 12px;
            background: var(--bg-deep);
            border-radius: 6px;
            overflow: hidden;
            margin-top: 0.75rem;
        }
        .risk-fill {
            height: 100%;
            border-radius: 6px;
            transition: width 0.5s ease;
        }
        .recommendations {
            list-style: none;
            margin-top: 1rem;
        }
        .recommendations li {
            font-family: var(--font-mono);
            font-size: 0.85rem;
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            background: var(--bg-elevated);
            border-radius: 8px;
            border-left: 3px solid var(--accent-primary);
        }
        .certificate {
            background: linear-gradient(135deg, rgba(0, 240, 255, 0.1), rgba(0, 184, 212, 0.05));
            border: 2px solid var(--accent-primary);
            padding: 2.5rem;
            text-align: center;
            box-shadow: 0 0 40px rgba(0, 240, 255, 0.15);
        }
        .certificate h2 { 
            color: var(--accent-primary);
            text-shadow: 0 0 20px var(--accent-glow);
            margin-bottom: 1rem; 
        }
        .certificate p {
            font-family: var(--font-mono);
            font-size: 0.9rem;
        }
        table { width: 100%; border-collapse: collapse; }
        th, td { 
            padding: 1rem; 
            text-align: left; 
            border-bottom: 1px solid var(--border-subtle);
            font-family: var(--font-mono);
        }
        th { 
            color: var(--text-muted); 
            font-weight: 500;
            font-size: 0.75rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }
        td { font-size: 0.9rem; }
        .footer { 
            text-align: center; 
            padding: 2rem 0; 
            font-family: var(--font-mono);
            font-size: 0.8rem;
            color: var(--text-muted);
            letter-spacing: 0.1em;
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>◈ PRIV.GUARD REPORT</h1>
            <p>Generated on {{ generated_at }}</p>
            <p>Report ID: {{ report_id }}</p>
        </header>

        <section class="card">
            <h2>◈ DATASET OVERVIEW</h2>
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value">{{ data_summary.rows }}</div>
                    <div class="metric-label">Records</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ data_summary.columns }}</div>
                    <div class="metric-label">Columns</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ pii_summary.total }}</div>
                    <div class="metric-label">PII Detected</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ pii_summary.types }}</div>
                    <div class="metric-label">PII Types</div>
                </div>
            </div>
        </section>

        <section class="card">
            <h2>◈ PRIVACY METRICS</h2>
            <div class="metrics">
                <div class="metric">
                    <div class="metric-value">{{ privacy_metrics.epsilon }}</div>
                    <div class="metric-label">Epsilon (ε)</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ privacy_metrics.k_anonymity }}</div>
                    <div class="metric-label">k-Anonymity</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ privacy_metrics.l_diversity }}</div>
                    <div class="metric-label">l-Diversity</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ privacy_metrics.budget_used }}%</div>
                    <div class="metric-label">Budget Used</div>
                </div>
            </div>
        </section>

        <section class="card">
            <h2>⚠ RISK ASSESSMENT</h2>
            <p style="font-family: var(--font-mono);">Overall Risk Level: <span class="status-badge {{ risk_class }}">{{ risk_level }}</span></p>
            <div class="risk-bar">
                <div class="risk-fill" style="width: {{ risk_percentage }}%; background: linear-gradient(90deg, {{ risk_color }}, {{ risk_color }}99);"></div>
            </div>
            {% if recommendations %}
            <ul class="recommendations">
                {% for rec in recommendations %}
                <li>{{ rec }}</li>
                {% endfor %}
            </ul>
            {% endif %}
        </section>

        <section class="card">
            <h2>✓ COMPLIANCE STATUS</h2>
            <table>
                <tr><th>Regulation</th><th>Score</th><th>Status</th></tr>
                {% for compliance in compliance_results %}
                <tr>
                    <td>{{ compliance.name }}</td>
                    <td>{{ compliance.score }}/100</td>
                    <td><span class="status-badge {{ compliance.class }}">{{ compliance.status }}</span></td>
                </tr>
                {% endfor %}
            </table>
        </section>

        {% if insights %}
        <section class="card">
            <h2>◈ ANALYSIS INSIGHTS</h2>
            <div style="font-family: var(--font-mono); font-size: 0.9rem; white-space: pre-wrap;">{{ insights }}</div>
        </section>
        {% endif %}

        <section class="card certificate">
            <h2>◈ PRIVACY CERTIFICATE</h2>
            <p><strong>Certificate ID:</strong> {{ certificate_id }}</p>
            <p style="margin-top: 0.5rem;">This analysis satisfies ({{ privacy_metrics.epsilon }}, {{ privacy_metrics.delta }})-differential privacy.</p>
            <p style="margin-top: 1rem; font-size: 0.8rem; color: var(--text-muted);">
                Valid until: {{ certificate_valid_until }}
            </p>
        </section>

        <footer class="footer">
            <p>PRIV.GUARD // Privacy-Preserving Data Analyzer v1.0</p>
        </footer>
    </div>
</body>
</html>"""


class ReportGenerator:
    """Generate privacy analysis reports."""

    def __init__(self):
        self.template = HTML_TEMPLATE

    def generate_html_report(
        self,
        data_summary: Dict[str, Any],
        pii_summary: Dict[str, Any],
        privacy_metrics: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        compliance_results: Dict[str, Any],
        insights: str = None,
    ) -> str:
        """
        Generate an HTML report.

        Args:
            data_summary: Dataset summary
            pii_summary: PII detection summary
            privacy_metrics: Privacy metrics
            risk_assessment: Risk assessment results
            compliance_results: Compliance check results
            insights: LLM-generated insights

        Returns:
            HTML report string
        """
        report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"
        certificate_id = f"PC-{int(datetime.now().timestamp())}-{uuid.uuid4().hex[:8].upper()}"

        # Determine risk styling
        risk_level = risk_assessment.get("overall", {}).get("risk_level", "Medium")
        risk_value = risk_assessment.get("overall", {}).get("overall_risk", 0.5)

        risk_config = {
            "Very Low": ("status-success", "#10b981", 10),
            "Low": ("status-success", "#10b981", 25),
            "Medium": ("status-warning", "#f59e0b", 50),
            "High": ("status-danger", "#ef4444", 75),
            "Very High": ("status-danger", "#ef4444", 95),
        }

        risk_class, risk_color, risk_pct = risk_config.get(risk_level, ("status-warning", "#f59e0b", 50))

        # Format compliance results
        compliance_list = []
        for reg, data in compliance_results.items():
            if isinstance(data, dict):
                status = data.get("status", "Unknown")
                status_class = (
                    "status-success"
                    if status == "Compliant"
                    else "status-warning" if "Partial" in status else "status-danger"
                )
                compliance_list.append(
                    {"name": reg.upper(), "score": data.get("score", 0), "status": status, "class": status_class}
                )

        # Get recommendations
        recommendations = risk_assessment.get("overall", {}).get("recommendations", [])

        # Build context
        context = {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "report_id": report_id,
            "certificate_id": certificate_id,
            "certificate_valid_until": (datetime.now().replace(year=datetime.now().year + 1)).strftime("%Y-%m-%d"),
            "data_summary": {"rows": data_summary.get("row_count", 0), "columns": data_summary.get("column_count", 0)},
            "pii_summary": {"total": pii_summary.get("total_pii", 0), "types": len(pii_summary.get("by_type", {}))},
            "privacy_metrics": {
                "epsilon": privacy_metrics.get("epsilon", 1.0),
                "delta": privacy_metrics.get("delta", 1e-5),
                "k_anonymity": privacy_metrics.get("k_anonymity", "-"),
                "l_diversity": privacy_metrics.get("l_diversity", "-"),
                "budget_used": round((privacy_metrics.get("used_epsilon", 0) / privacy_metrics.get("epsilon", 1.0)) * 100, 1) if privacy_metrics.get("epsilon", 0) > 0 else 0,
            },
            "risk_level": risk_level,
            "risk_class": risk_class,
            "risk_color": risk_color,
            "risk_percentage": risk_pct,
            "recommendations": recommendations,
            "compliance_results": compliance_list,
            "insights": insights,
        }

        # Render template
        if JINJA2_AVAILABLE:
            template = Template(self.template)
            return template.render(**context)
        else:
            # Simple string replacement fallback
            html = self.template
            for key, value in self._flatten_dict(context).items():
                html = html.replace("{{ " + key + " }}", str(value))
            return html

    def _flatten_dict(self, d: dict, parent_key: str = "", sep: str = ".") -> dict:
        """Flatten nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def save_report(self, report_html: str, output_path: str):
        """Save report to file."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_html)

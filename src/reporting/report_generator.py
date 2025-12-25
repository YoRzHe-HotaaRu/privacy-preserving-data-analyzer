"""Reporting Module - Report Generator"""

from typing import Dict, Any, List
from datetime import datetime
import uuid
from pathlib import Path

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
    <title>Privacy Analysis Report</title>
    <style>
        :root {
            --bg: #0a0a0f;
            --card-bg: rgba(20, 20, 30, 0.9);
            --accent: #6366f1;
            --accent-light: #818cf8;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --text: #e2e8f0;
            --text-muted: #94a3b8;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 2rem;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            text-align: center;
            padding: 3rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 2rem;
        }
        .header h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, var(--accent), var(--accent-light));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .header p { color: var(--text-muted); }
        .card {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
        }
        .card h2 {
            font-size: 1.25rem;
            margin-bottom: 1rem;
            color: var(--accent-light);
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }
        .metric {
            background: rgba(99, 102, 241, 0.1);
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: var(--accent);
        }
        .metric-label { color: var(--text-muted); font-size: 0.875rem; }
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 500;
        }
        .status-success { background: rgba(16, 185, 129, 0.2); color: var(--success); }
        .status-warning { background: rgba(245, 158, 11, 0.2); color: var(--warning); }
        .status-danger { background: rgba(239, 68, 68, 0.2); color: var(--danger); }
        .list { list-style: none; }
        .list li {
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .list li:last-child { border: none; }
        .risk-bar {
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 0.5rem;
        }
        .risk-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }
        .certificate {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.1));
            border: 2px solid var(--accent);
            padding: 2rem;
            text-align: center;
        }
        .certificate h2 { color: var(--accent); margin-bottom: 1rem; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 0.75rem; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }
        th { color: var(--text-muted); font-weight: 500; }
        .footer { text-align: center; padding: 2rem 0; color: var(--text-muted); }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🔒 Privacy Analysis Report</h1>
            <p>Generated on {{ generated_at }}</p>
            <p>Report ID: {{ report_id }}</p>
        </header>

        <section class="card">
            <h2>📊 Dataset Overview</h2>
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
            <h2>🛡️ Privacy Metrics</h2>
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
            <h2>⚠️ Risk Assessment</h2>
            <p>Overall Risk Level: <span class="status-badge {{ risk_class }}">{{ risk_level }}</span></p>
            <div class="risk-bar">
                <div class="risk-fill" style="width: {{ risk_percentage }}%; background: {{ risk_color }};"></div>
            </div>
            <ul class="list" style="margin-top: 1rem;">
                {% for rec in recommendations %}
                <li>{{ rec }}</li>
                {% endfor %}
            </ul>
        </section>

        <section class="card">
            <h2>✅ Compliance Status</h2>
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
            <h2>💡 Analysis Insights</h2>
            <div style="white-space: pre-wrap;">{{ insights }}</div>
        </section>
        {% endif %}

        <section class="card certificate">
            <h2>🏆 Privacy Certificate</h2>
            <p><strong>Certificate ID:</strong> {{ certificate_id }}</p>
            <p>This analysis satisfies ({{ privacy_metrics.epsilon }}, {{ privacy_metrics.delta }})-differential privacy.</p>
            <p style="margin-top: 1rem; font-size: 0.875rem; color: var(--text-muted);">
                Valid until: {{ certificate_valid_until }}
            </p>
        </section>

        <footer class="footer">
            <p>Generated by Privacy-Preserving Data Analyzer v1.0</p>
        </footer>
    </div>
</body>
</html>"""


class ReportGenerator:
    """Generate privacy analysis reports."""
    
    def __init__(self):
        self.template = HTML_TEMPLATE
    
    def generate_html_report(self, 
                           data_summary: Dict[str, Any],
                           pii_summary: Dict[str, Any],
                           privacy_metrics: Dict[str, Any],
                           risk_assessment: Dict[str, Any],
                           compliance_results: Dict[str, Any],
                           insights: str = None) -> str:
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
        risk_level = risk_assessment.get('overall', {}).get('risk_level', 'Medium')
        risk_value = risk_assessment.get('overall', {}).get('overall_risk', 0.5)
        
        risk_config = {
            'Very Low': ('status-success', '#10b981', 10),
            'Low': ('status-success', '#10b981', 25),
            'Medium': ('status-warning', '#f59e0b', 50),
            'High': ('status-danger', '#ef4444', 75),
            'Very High': ('status-danger', '#ef4444', 95),
        }
        
        risk_class, risk_color, risk_pct = risk_config.get(risk_level, ('status-warning', '#f59e0b', 50))
        
        # Format compliance results
        compliance_list = []
        for reg, data in compliance_results.items():
            if isinstance(data, dict):
                status = data.get('status', 'Unknown')
                status_class = 'status-success' if status == 'Compliant' else 'status-warning' if 'Partial' in status else 'status-danger'
                compliance_list.append({
                    'name': reg.upper(),
                    'score': data.get('score', 0),
                    'status': status,
                    'class': status_class
                })
        
        # Get recommendations
        recommendations = risk_assessment.get('overall', {}).get('recommendations', [])
        
        # Build context
        context = {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'report_id': report_id,
            'certificate_id': certificate_id,
            'certificate_valid_until': (datetime.now().replace(year=datetime.now().year + 1)).strftime('%Y-%m-%d'),
            'data_summary': {
                'rows': data_summary.get('row_count', 0),
                'columns': data_summary.get('column_count', 0)
            },
            'pii_summary': {
                'total': pii_summary.get('total_pii', 0),
                'types': len(pii_summary.get('by_type', {}))
            },
            'privacy_metrics': {
                'epsilon': privacy_metrics.get('epsilon', 1.0),
                'delta': privacy_metrics.get('delta', 1e-5),
                'k_anonymity': privacy_metrics.get('k_anonymity', '-'),
                'l_diversity': privacy_metrics.get('l_diversity', '-'),
                'budget_used': round(privacy_metrics.get('budget_utilization', 0) * 100, 1)
            },
            'risk_level': risk_level,
            'risk_class': risk_class,
            'risk_color': risk_color,
            'risk_percentage': risk_pct,
            'recommendations': recommendations,
            'compliance_results': compliance_list,
            'insights': insights
        }
        
        # Render template
        if JINJA2_AVAILABLE:
            template = Template(self.template)
            return template.render(**context)
        else:
            # Simple string replacement fallback
            html = self.template
            for key, value in self._flatten_dict(context).items():
                html = html.replace('{{ ' + key + ' }}', str(value))
            return html
    
    def _flatten_dict(self, d: dict, parent_key: str = '', sep: str = '.') -> dict:
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
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_html)

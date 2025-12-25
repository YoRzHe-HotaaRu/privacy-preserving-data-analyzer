"""Reporting Module - Privacy Certificate Generator"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict


def generate_certificate_id() -> str:
    """Generate unique certificate ID."""
    timestamp = int(datetime.now().timestamp())
    unique_id = uuid.uuid4().hex[:8]
    return f"PC-{timestamp}-{unique_id}".upper()


def generate_privacy_certificate(
    analysis_metadata: Dict[str, Any], privacy_metrics: Dict[str, Any], compliance_results: Dict[str, Any]
) -> str:
    """
    Generate detailed privacy certificate.

    Args:
        analysis_metadata: Analysis metadata
        privacy_metrics: Privacy metrics
        compliance_results: Compliance results

    Returns:
        Privacy certificate text
    """
    certificate_id = generate_certificate_id()

    # Build anonymization methods list
    anon_methods = privacy_metrics.get("anonymization_methods", ["masking", "suppression"])
    methods_str = "\n".join([f"  • {method}" for method in anon_methods])

    # Build compliance scores
    compliance_str = ""
    for reg, data in compliance_results.items():
        if isinstance(data, dict) and "score" in data:
            compliance_str += f"  • {reg.upper()}: {data['score']}/100 ({data.get('status', 'Unknown')})\n"

    certificate = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           PRIVACY CERTIFICATE                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

Certificate ID: {certificate_id}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
Valid Until: {(datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')}

┌──────────────────────────────────────────────────────────────────────────────┐
│ ANALYSIS METADATA                                                            │
├──────────────────────────────────────────────────────────────────────────────┤
│ Analysis ID:        {analysis_metadata.get('analysis_id', 'N/A'):<40}         │
│ Dataset Name:       {analysis_metadata.get('dataset_name', 'N/A'):<40}         │
│ Record Count:       {analysis_metadata.get('record_count', 0):<40,}            │
│ Analysis Date:      {analysis_metadata.get('analysis_date', 'N/A'):<40}        │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ PRIVACY GUARANTEES                                                           │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ Differential Privacy Parameters:                                             │
│   Epsilon (ε):      {privacy_metrics.get('epsilon', 0):.4f}                   │
│   Delta (δ):        {privacy_metrics.get('delta', 0):.6f}                     │
│                                                                              │
│   This analysis satisfies ({privacy_metrics.get('epsilon', 0):.4f},          │
│   {privacy_metrics.get('delta', 0):.6f})-differential privacy.               │
│                                                                              │
│ Privacy Model Metrics:                                                       │
│   k-Anonymity:      {privacy_metrics.get('k_anonymity', 'N/A')}               │
│   l-Diversity:      {privacy_metrics.get('l_diversity', 'N/A')}               │
│   t-Closeness:      {privacy_metrics.get('t_closeness', 'N/A')}               │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ ANONYMIZATION METHODS APPLIED                                                │
├──────────────────────────────────────────────────────────────────────────────┤
{methods_str}
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ COMPLIANCE ASSESSMENT                                                        │
├──────────────────────────────────────────────────────────────────────────────┤
{compliance_str}└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ DISCLAIMER                                                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│ This certificate certifies that the analysis was performed with the stated  │
│ privacy guarantees. Privacy is not absolute - residual risks may exist.     │
│ Compliance scores are automated assessments and should be reviewed by       │
│ legal professionals before regulatory reliance.                             │
└──────────────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════╗
║  End of Privacy Certificate                                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    return certificate

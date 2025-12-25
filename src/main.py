"""
Privacy-Preserving Data Analyzer - Main Entry Point
====================================================
A comprehensive system for analyzing sensitive data while protecting privacy.
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from anonymization import DataAnonymizer
from data_ingestion import load_file
from differential_privacy import DifferentialPrivacyEngine
from pii_detection import PIIDetector
from reporting import ReportGenerator, generate_privacy_certificate
from risk_assessment import ComplianceChecker, RiskCalculator


def analyze_data(
    input_path: str,
    output_path: str = None,
    epsilon: float = 1.0,
    delta: float = 1e-5,
    quasi_identifiers: list = None,
    sensitive_attribute: str = None,
):
    """
    Run complete privacy-preserving analysis on a dataset.

    Args:
        input_path: Path to input data file
        output_path: Path to save report (optional)
        epsilon: Privacy budget
        delta: Delta parameter
        quasi_identifiers: List of quasi-identifier columns
        sensitive_attribute: Sensitive attribute column

    Returns:
        Analysis results dictionary
    """
    print(f"🔒 Privacy-Preserving Data Analyzer")
    print(f"=" * 50)
    print(f"Input: {input_path}")
    print(f"Epsilon: {epsilon}, Delta: {delta}")
    print()

    # Step 1: Load data
    print("📊 Loading data...")
    df = load_file(input_path)
    print(f"   Loaded {len(df)} rows, {len(df.columns)} columns")

    # Step 2: Detect PII
    print("\n🔍 Detecting PII...")
    pii_detector = PIIDetector()
    pii_summary = {"total_pii": 0, "by_type": {}}
    pii_columns = {}

    for col in df.columns:
        sample = df[col].dropna().head(10).astype(str).tolist()
        col_pii = []
        for val in sample:
            detected = pii_detector.detect(val)
            col_pii.extend(detected)

        if col_pii:
            entity_type = col_pii[0]["entity_type"]
            pii_columns[col] = entity_type
            pii_summary["total_pii"] += len(col_pii)
            pii_summary["by_type"][col] = {"entity_type": entity_type, "count": len(col_pii)}
            print(f"   {col}: {len(col_pii)} instances of {entity_type}")

    if not pii_columns:
        print("   No PII detected")

    # Step 3: Anonymize data
    print("\n🎭 Anonymizing data...")
    anonymizer = DataAnonymizer()
    anonymized_df = anonymizer.anonymize_dataframe(df, pii_columns)
    print(f"   Anonymized {len(pii_columns)} columns")

    # Step 4: Apply differential privacy
    print("\n🔐 Applying differential privacy...")
    dp_engine = DifferentialPrivacyEngine(epsilon=epsilon, delta=delta)
    budget_report = dp_engine.get_budget_report()
    print(f"   Privacy budget: ε={epsilon}, δ={delta}")

    # Step 5: Risk assessment
    print("\n⚠️ Assessing privacy risks...")
    risk_calculator = RiskCalculator()

    if quasi_identifiers:
        qi_list = [q for q in quasi_identifiers if q in df.columns]
        if qi_list:
            risk_results = risk_calculator.calculate_all_metrics(df, qi_list, sensitive_attribute)
            print(f"   k-Anonymity: {risk_results.get('k_anonymity', {}).get('k', 'N/A')}")
            print(f"   Risk Level: {risk_results.get('overall', {}).get('risk_level', 'N/A')}")
        else:
            risk_results = {"overall": {"risk_level": "Unknown", "recommendations": []}}
    else:
        risk_results = {"overall": {"risk_level": "Unknown", "recommendations": []}}

    # Step 6: Compliance check
    print("\n✅ Checking compliance...")
    compliance_checker = ComplianceChecker()
    compliance = compliance_checker.check_all(risk_results, pii_summary, True)
    print(f"   GDPR: {compliance['gdpr']['score']}/100 ({compliance['gdpr']['status']})")
    print(f"   CCPA: {compliance['ccpa']['score']}/100 ({compliance['ccpa']['status']})")

    # Step 7: Generate report
    print("\n📄 Generating report...")
    report_generator = ReportGenerator()

    data_summary = {"row_count": len(df), "column_count": len(df.columns)}

    privacy_metrics = {
        "epsilon": epsilon,
        "delta": delta,
        "k_anonymity": risk_results.get("k_anonymity", {}).get("k", "N/A"),
        "l_diversity": risk_results.get("l_diversity", {}).get("l", "N/A"),
        "budget_utilization": budget_report.get("budget_utilization", 0),
    }

    html_report = report_generator.generate_html_report(
        data_summary, pii_summary, privacy_metrics, risk_results, compliance
    )

    if output_path:
        report_generator.save_report(html_report, output_path)
        print(f"   Report saved to: {output_path}")

    # Step 8: Generate certificate
    print("\n🏆 Generating privacy certificate...")
    analysis_metadata = {
        "analysis_id": f"ANA-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "dataset_name": Path(input_path).name,
        "record_count": len(df),
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    certificate = generate_privacy_certificate(analysis_metadata, privacy_metrics, compliance)

    print("\n" + "=" * 50)
    print("✅ Analysis complete!")

    return {
        "anonymized_data": anonymized_df,
        "pii_summary": pii_summary,
        "privacy_metrics": privacy_metrics,
        "risk_assessment": risk_results,
        "compliance": compliance,
        "certificate": certificate,
    }


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the FastAPI server."""
    import uvicorn

    from web.app import app

    print(f"🚀 Starting Privacy-Preserving Data Analyzer server...")
    print(f"   Open http://localhost:{port} in your browser")
    uvicorn.run(app, host=host, port=port)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Privacy-Preserving Data Analyzer", formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a data file")
    analyze_parser.add_argument("--input", "-i", required=True, help="Input file path")
    analyze_parser.add_argument("--output", "-o", help="Output report path")
    analyze_parser.add_argument("--epsilon", "-e", type=float, default=1.0, help="Privacy budget")
    analyze_parser.add_argument("--delta", "-d", type=float, default=1e-5, help="Delta parameter")
    analyze_parser.add_argument("--quasi", "-q", help="Quasi-identifiers (comma-separated)")
    analyze_parser.add_argument("--sensitive", "-s", help="Sensitive attribute column")

    # Server command
    server_parser = subparsers.add_parser("server", help="Run web server")
    server_parser.add_argument("--host", default="0.0.0.0", help="Host address")
    server_parser.add_argument("--port", "-p", type=int, default=8000, help="Port number")

    args = parser.parse_args()

    if args.command == "analyze":
        quasi = args.quasi.split(",") if args.quasi else None
        analyze_data(args.input, args.output, args.epsilon, args.delta, quasi, args.sensitive)
    elif args.command == "server":
        run_server(args.host, args.port)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

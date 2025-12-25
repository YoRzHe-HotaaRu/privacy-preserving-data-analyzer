"""Unit tests for reporting module."""

import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from reporting.privacy_certificate import generate_certificate_id, generate_privacy_certificate
from reporting.report_generator import HTML_TEMPLATE, ReportGenerator


class TestReportGenerator:
    """Test HTML report generation."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up report generator for each test."""
        self.generator = ReportGenerator()

    @pytest.fixture
    def sample_data_summary(self):
        """Sample data summary."""
        return {"row_count": 1000, "column_count": 10}

    @pytest.fixture
    def sample_pii_summary(self):
        """Sample PII summary."""
        return {
            "total_pii": 150,
            "by_type": {
                "email": {"entity_type": "EMAIL_ADDRESS", "count": 100},
                "name": {"entity_type": "PERSON", "count": 50},
            },
        }

    @pytest.fixture
    def sample_privacy_metrics(self):
        """Sample privacy metrics."""
        return {"epsilon": 1.0, "delta": 1e-5, "k_anonymity": 5, "l_diversity": 3, "budget_utilization": 0.25}

    @pytest.fixture
    def sample_risk_assessment(self):
        """Sample risk assessment."""
        return {
            "overall": {
                "risk_level": "Low",
                "overall_risk": 0.2,
                "recommendations": ["Consider increasing k-anonymity", "Review sensitive attributes"],
            },
            "k_anonymity": {"k": 5},
        }

    @pytest.fixture
    def sample_compliance_results(self):
        """Sample compliance results."""
        return {
            "gdpr": {"score": 85, "status": "Compliant"},
            "ccpa": {"score": 90, "status": "Compliant"},
            "hipaa": {"score": 75, "status": "Partial Compliance"},
        }

    def test_generate_html_report_basic(
        self,
        sample_data_summary,
        sample_pii_summary,
        sample_privacy_metrics,
        sample_risk_assessment,
        sample_compliance_results,
    ):
        """Test basic HTML report generation."""
        html = self.generator.generate_html_report(
            sample_data_summary,
            sample_pii_summary,
            sample_privacy_metrics,
            sample_risk_assessment,
            sample_compliance_results,
        )

        assert isinstance(html, str)
        assert len(html) > 0
        assert "<!DOCTYPE html>" in html
        assert "</html>" in html

    def test_report_contains_data_summary(
        self,
        sample_data_summary,
        sample_pii_summary,
        sample_privacy_metrics,
        sample_risk_assessment,
        sample_compliance_results,
    ):
        """Test that report contains data summary."""
        html = self.generator.generate_html_report(
            sample_data_summary,
            sample_pii_summary,
            sample_privacy_metrics,
            sample_risk_assessment,
            sample_compliance_results,
        )

        assert "1000" in html or "1,000" in html  # row count
        assert "10" in html  # column count

    def test_report_contains_pii_info(
        self,
        sample_data_summary,
        sample_pii_summary,
        sample_privacy_metrics,
        sample_risk_assessment,
        sample_compliance_results,
    ):
        """Test that report contains PII information."""
        html = self.generator.generate_html_report(
            sample_data_summary,
            sample_pii_summary,
            sample_privacy_metrics,
            sample_risk_assessment,
            sample_compliance_results,
        )

        assert "150" in html  # total PII

    def test_report_contains_privacy_metrics(
        self,
        sample_data_summary,
        sample_pii_summary,
        sample_privacy_metrics,
        sample_risk_assessment,
        sample_compliance_results,
    ):
        """Test that report contains privacy metrics."""
        html = self.generator.generate_html_report(
            sample_data_summary,
            sample_pii_summary,
            sample_privacy_metrics,
            sample_risk_assessment,
            sample_compliance_results,
        )

        assert "Epsilon" in html or "epsilon" in html or "ε" in html
        assert "1.0" in html or "1" in html  # epsilon value

    def test_report_contains_compliance_info(
        self,
        sample_data_summary,
        sample_pii_summary,
        sample_privacy_metrics,
        sample_risk_assessment,
        sample_compliance_results,
    ):
        """Test that report contains compliance information."""
        html = self.generator.generate_html_report(
            sample_data_summary,
            sample_pii_summary,
            sample_privacy_metrics,
            sample_risk_assessment,
            sample_compliance_results,
        )

        assert "GDPR" in html
        assert "CCPA" in html
        assert "HIPAA" in html

    def test_report_contains_risk_level(
        self,
        sample_data_summary,
        sample_pii_summary,
        sample_privacy_metrics,
        sample_risk_assessment,
        sample_compliance_results,
    ):
        """Test that report contains risk assessment."""
        html = self.generator.generate_html_report(
            sample_data_summary,
            sample_pii_summary,
            sample_privacy_metrics,
            sample_risk_assessment,
            sample_compliance_results,
        )

        assert "Low" in html or "Risk" in html

    def test_report_with_insights(
        self,
        sample_data_summary,
        sample_pii_summary,
        sample_privacy_metrics,
        sample_risk_assessment,
        sample_compliance_results,
    ):
        """Test report generation with LLM insights."""
        insights = "This dataset contains customer information with moderate privacy risk."

        html = self.generator.generate_html_report(
            sample_data_summary,
            sample_pii_summary,
            sample_privacy_metrics,
            sample_risk_assessment,
            sample_compliance_results,
            insights=insights,
        )

        assert insights in html or "Insights" in html

    def test_report_has_valid_html_structure(
        self,
        sample_data_summary,
        sample_pii_summary,
        sample_privacy_metrics,
        sample_risk_assessment,
        sample_compliance_results,
    ):
        """Test that report has valid HTML structure."""
        html = self.generator.generate_html_report(
            sample_data_summary,
            sample_pii_summary,
            sample_privacy_metrics,
            sample_risk_assessment,
            sample_compliance_results,
        )

        assert "<html" in html
        assert "<head>" in html
        assert "<body>" in html
        assert "</body>" in html
        assert "<title>" in html

    def test_report_has_styling(
        self,
        sample_data_summary,
        sample_pii_summary,
        sample_privacy_metrics,
        sample_risk_assessment,
        sample_compliance_results,
    ):
        """Test that report includes CSS styling."""
        html = self.generator.generate_html_report(
            sample_data_summary,
            sample_pii_summary,
            sample_privacy_metrics,
            sample_risk_assessment,
            sample_compliance_results,
        )

        assert "<style>" in html
        assert "</style>" in html

    def test_report_id_generated(
        self,
        sample_data_summary,
        sample_pii_summary,
        sample_privacy_metrics,
        sample_risk_assessment,
        sample_compliance_results,
    ):
        """Test that report ID is generated."""
        html = self.generator.generate_html_report(
            sample_data_summary,
            sample_pii_summary,
            sample_privacy_metrics,
            sample_risk_assessment,
            sample_compliance_results,
        )

        assert "RPT-" in html

    def test_save_report(
        self,
        sample_data_summary,
        sample_pii_summary,
        sample_privacy_metrics,
        sample_risk_assessment,
        sample_compliance_results,
    ):
        """Test saving report to file."""
        html = self.generator.generate_html_report(
            sample_data_summary,
            sample_pii_summary,
            sample_privacy_metrics,
            sample_risk_assessment,
            sample_compliance_results,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "report.html")
            self.generator.save_report(html, output_path)

            assert os.path.exists(output_path)
            with open(output_path, "r", encoding="utf-8") as f:
                saved_content = f.read()
            assert saved_content == html

    def test_save_report_creates_directory(
        self,
        sample_data_summary,
        sample_pii_summary,
        sample_privacy_metrics,
        sample_risk_assessment,
        sample_compliance_results,
    ):
        """Test that save_report creates parent directories."""
        html = self.generator.generate_html_report(
            sample_data_summary,
            sample_pii_summary,
            sample_privacy_metrics,
            sample_risk_assessment,
            sample_compliance_results,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "nested", "dir", "report.html")
            self.generator.save_report(html, output_path)

            assert os.path.exists(output_path)

    def test_flatten_dict(self):
        """Test dictionary flattening."""
        nested = {"a": 1, "b": {"c": 2, "d": 3}}

        flattened = self.generator._flatten_dict(nested)

        assert flattened["a"] == 1
        assert flattened["b.c"] == 2
        assert flattened["b.d"] == 3

    def test_risk_level_styling(
        self, sample_data_summary, sample_pii_summary, sample_privacy_metrics, sample_compliance_results
    ):
        """Test different risk level styling."""
        risk_levels = ["Very Low", "Low", "Medium", "High", "Very High"]

        for level in risk_levels:
            risk_assessment = {"overall": {"risk_level": level, "overall_risk": 0.5, "recommendations": []}}

            html = self.generator.generate_html_report(
                sample_data_summary,
                sample_pii_summary,
                sample_privacy_metrics,
                risk_assessment,
                sample_compliance_results,
            )

            assert level in html


class TestPrivacyCertificate:
    """Test privacy certificate generation."""

    @pytest.fixture
    def sample_analysis_metadata(self):
        """Sample analysis metadata."""
        return {
            "analysis_id": "ANA-20231225120000",
            "dataset_name": "customer_data.csv",
            "record_count": 1000,
            "analysis_date": "2023-12-25 12:00:00",
        }

    @pytest.fixture
    def sample_privacy_metrics(self):
        """Sample privacy metrics."""
        return {
            "epsilon": 1.0,
            "delta": 1e-5,
            "k_anonymity": 5,
            "l_diversity": 3,
            "t_closeness": 0.1,
            "anonymization_methods": ["masking", "suppression", "generalization"],
        }

    @pytest.fixture
    def sample_compliance_results(self):
        """Sample compliance results."""
        return {"gdpr": {"score": 85, "status": "Compliant"}, "ccpa": {"score": 90, "status": "Compliant"}}

    def test_generate_certificate_id_format(self):
        """Test certificate ID format."""
        cert_id = generate_certificate_id()

        assert cert_id.startswith("PC-")
        assert len(cert_id) > 10
        assert cert_id.isupper()

    def test_generate_certificate_id_unique(self):
        """Test certificate ID uniqueness."""
        ids = [generate_certificate_id() for _ in range(10)]

        # All IDs should be unique
        assert len(set(ids)) == len(ids)

    def test_generate_privacy_certificate(
        self, sample_analysis_metadata, sample_privacy_metrics, sample_compliance_results
    ):
        """Test privacy certificate generation."""
        certificate = generate_privacy_certificate(
            sample_analysis_metadata, sample_privacy_metrics, sample_compliance_results
        )

        assert isinstance(certificate, str)
        assert len(certificate) > 0

    def test_certificate_contains_metadata(
        self, sample_analysis_metadata, sample_privacy_metrics, sample_compliance_results
    ):
        """Test certificate contains analysis metadata."""
        certificate = generate_privacy_certificate(
            sample_analysis_metadata, sample_privacy_metrics, sample_compliance_results
        )

        assert "ANA-20231225120000" in certificate or "Analysis ID" in certificate
        assert "customer_data.csv" in certificate or "Dataset" in certificate

    def test_certificate_contains_privacy_params(
        self, sample_analysis_metadata, sample_privacy_metrics, sample_compliance_results
    ):
        """Test certificate contains privacy parameters."""
        certificate = generate_privacy_certificate(
            sample_analysis_metadata, sample_privacy_metrics, sample_compliance_results
        )

        assert "Epsilon" in certificate or "epsilon" in certificate or "ε" in certificate
        assert "Delta" in certificate or "delta" in certificate or "δ" in certificate

    def test_certificate_contains_compliance(
        self, sample_analysis_metadata, sample_privacy_metrics, sample_compliance_results
    ):
        """Test certificate contains compliance info."""
        certificate = generate_privacy_certificate(
            sample_analysis_metadata, sample_privacy_metrics, sample_compliance_results
        )

        assert "GDPR" in certificate
        assert "CCPA" in certificate

    def test_certificate_contains_anonymization_methods(
        self, sample_analysis_metadata, sample_privacy_metrics, sample_compliance_results
    ):
        """Test certificate contains anonymization methods."""
        certificate = generate_privacy_certificate(
            sample_analysis_metadata, sample_privacy_metrics, sample_compliance_results
        )

        assert "masking" in certificate or "ANONYMIZATION" in certificate

    def test_certificate_has_disclaimer(
        self, sample_analysis_metadata, sample_privacy_metrics, sample_compliance_results
    ):
        """Test certificate contains disclaimer."""
        certificate = generate_privacy_certificate(
            sample_analysis_metadata, sample_privacy_metrics, sample_compliance_results
        )

        assert "DISCLAIMER" in certificate

    def test_certificate_has_validity_period(
        self, sample_analysis_metadata, sample_privacy_metrics, sample_compliance_results
    ):
        """Test certificate includes validity period."""
        certificate = generate_privacy_certificate(
            sample_analysis_metadata, sample_privacy_metrics, sample_compliance_results
        )

        assert "Valid Until" in certificate

    def test_certificate_format_structure(
        self, sample_analysis_metadata, sample_privacy_metrics, sample_compliance_results
    ):
        """Test certificate has proper formatting structure."""
        certificate = generate_privacy_certificate(
            sample_analysis_metadata, sample_privacy_metrics, sample_compliance_results
        )

        # Should have box drawing characters
        assert "╔" in certificate or "┌" in certificate
        assert "PRIVACY CERTIFICATE" in certificate


class TestHTMLTemplate:
    """Test HTML template validity."""

    def test_template_is_string(self):
        """Test template is a string."""
        assert isinstance(HTML_TEMPLATE, str)

    def test_template_has_html_structure(self):
        """Test template has basic HTML structure."""
        assert "<!DOCTYPE html>" in HTML_TEMPLATE
        assert "<html" in HTML_TEMPLATE
        assert "<head>" in HTML_TEMPLATE
        assert "<body>" in HTML_TEMPLATE

    def test_template_has_jinja_placeholders(self):
        """Test template has Jinja2 placeholders."""
        assert "{{" in HTML_TEMPLATE
        assert "}}" in HTML_TEMPLATE

    def test_template_has_styling(self):
        """Test template includes CSS styling."""
        assert "<style>" in HTML_TEMPLATE
        assert "var(--" in HTML_TEMPLATE  # CSS variables

    def test_template_is_responsive(self):
        """Test template has responsive viewport meta."""
        assert "viewport" in HTML_TEMPLATE

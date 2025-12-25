"""Risk Assessment Module - Compliance Checker"""

from typing import Any, Dict, List


class ComplianceChecker:
    """Check compliance with privacy regulations."""

    def check_gdpr(
        self, privacy_metrics: Dict[str, Any], pii_summary: Dict[str, Any], anonymization_applied: bool
    ) -> Dict[str, Any]:
        """
        Check GDPR compliance.

        Args:
            privacy_metrics: Privacy metrics from risk calculator
            pii_summary: Summary of detected PII
            anonymization_applied: Whether anonymization was applied

        Returns:
            Compliance assessment
        """
        score = 100
        issues = []
        recommendations = []

        # Data minimization
        if pii_summary.get("total_pii", 0) > 0 and not anonymization_applied:
            score -= 30
            issues.append("PII detected but not anonymized")
            recommendations.append("Apply anonymization to all PII fields")

        # k-anonymity check
        k_anon = privacy_metrics.get("k_anonymity", {})
        k = k_anon.get("k", 0)
        if k < 2:
            score -= 25
            issues.append("k-anonymity below minimum threshold")
            recommendations.append("Increase k-anonymity to at least 2")
        elif k < 5:
            score -= 10
            recommendations.append("Consider increasing k to 5+ for better protection")

        # Re-identification risk
        reid = privacy_metrics.get("re_identification", {})
        if reid.get("overall_risk", 0) > 0.5:
            score -= 20
            issues.append("High re-identification risk")
            recommendations.append("Apply additional anonymization techniques")

        # Determine status
        if score >= 80:
            status = "Compliant"
        elif score >= 60:
            status = "Partially Compliant"
        else:
            status = "Non-Compliant"

        return {
            "regulation": "GDPR",
            "score": max(0, score),
            "status": status,
            "issues": issues,
            "recommendations": recommendations,
        }

    def check_hipaa(
        self, privacy_metrics: Dict[str, Any], pii_summary: Dict[str, Any], anonymization_applied: bool
    ) -> Dict[str, Any]:
        """
        Check HIPAA compliance (for health data).

        HIPAA has specific requirements for Protected Health Information (PHI).
        """
        score = 100
        issues = []
        recommendations = []

        # PHI detection (medical-related PII)
        by_type = pii_summary.get("by_type", {})
        medical_pii = ["MEDICAL_ID", "DATE_OF_BIRTH", "LOCATION", "PHONE_NUMBER", "EMAIL_ADDRESS"]

        for pii_type in medical_pii:
            if pii_type in by_type and not anonymization_applied:
                score -= 15
                issues.append(f"{pii_type} detected (potential PHI)")

        # Safe Harbor method requires removal of 18 identifiers
        if len(by_type) > 5 and not anonymization_applied:
            score -= 20
            issues.append("Multiple identifier types detected")
            recommendations.append("Apply Safe Harbor de-identification method")

        # k-anonymity for HIPAA should be higher
        k_anon = privacy_metrics.get("k_anonymity", {})
        k = k_anon.get("k", 0)
        if k < 5:
            score -= 20
            issues.append("k-anonymity below HIPAA recommended threshold")
            recommendations.append("Increase k-anonymity to at least 5 for HIPAA")

        if score >= 80:
            status = "Compliant"
        elif score >= 60:
            status = "Partially Compliant"
        else:
            status = "Non-Compliant"

        return {
            "regulation": "HIPAA",
            "score": max(0, score),
            "status": status,
            "issues": issues,
            "recommendations": recommendations,
        }

    def check_ccpa(
        self, privacy_metrics: Dict[str, Any], pii_summary: Dict[str, Any], anonymization_applied: bool
    ) -> Dict[str, Any]:
        """
        Check CCPA compliance (California Consumer Privacy Act).
        """
        score = 100
        issues = []
        recommendations = []

        # Personal information detection
        if pii_summary.get("total_pii", 0) > 0:
            if not anonymization_applied:
                score -= 25
                issues.append("Personal information not de-identified")
                recommendations.append("De-identify personal information")

        # Re-identification risk
        reid = privacy_metrics.get("re_identification", {})
        if reid.get("overall_risk", 0) > 0.3:
            score -= 20
            issues.append("Re-identification risk above threshold")
            recommendations.append("Ensure data cannot be re-identified")

        if score >= 80:
            status = "Compliant"
        elif score >= 60:
            status = "Partially Compliant"
        else:
            status = "Non-Compliant"

        return {
            "regulation": "CCPA",
            "score": max(0, score),
            "status": status,
            "issues": issues,
            "recommendations": recommendations,
        }

    def check_all(
        self, privacy_metrics: Dict[str, Any], pii_summary: Dict[str, Any], anonymization_applied: bool = True
    ) -> Dict[str, Any]:
        """
        Check compliance with all regulations.

        Args:
            privacy_metrics: Privacy metrics from risk calculator
            pii_summary: Summary of detected PII
            anonymization_applied: Whether anonymization was applied

        Returns:
            Compliance assessment for all regulations
        """
        return {
            "gdpr": self.check_gdpr(privacy_metrics, pii_summary, anonymization_applied),
            "hipaa": self.check_hipaa(privacy_metrics, pii_summary, anonymization_applied),
            "ccpa": self.check_ccpa(privacy_metrics, pii_summary, anonymization_applied),
            "overall_compliant": all(
                [
                    self.check_gdpr(privacy_metrics, pii_summary, anonymization_applied)["status"] == "Compliant",
                    self.check_ccpa(privacy_metrics, pii_summary, anonymization_applied)["status"] == "Compliant",
                ]
            ),
        }

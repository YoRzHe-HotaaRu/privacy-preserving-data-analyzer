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

        total_pii = pii_summary.get("total_pii", 0)
        
        # Data minimization - PII count affects score
        if total_pii > 0:
            if not anonymization_applied:
                score -= 30
                issues.append("PII detected but not anonymized")
                recommendations.append("Apply anonymization to all PII fields")
            else:
                # Even with anonymization, high PII count is a concern
                if total_pii > 50:
                    score -= 10
                    recommendations.append("Consider reducing collected PII fields")
                elif total_pii > 100:
                    score -= 15
                    recommendations.append("High volume of PII - review data minimization")

        # k-anonymity check - check nested structure
        k_anon = privacy_metrics.get("k_anonymity", {})
        k = k_anon.get("k", 0) if isinstance(k_anon, dict) else 0
        
        if k > 0:  # Only penalize if we have k-anonymity data
            if k < 2:
                score -= 25
                issues.append(f"k-anonymity is {k} (below minimum threshold of 2)")
                recommendations.append("Increase k-anonymity to at least 2")
            elif k < 5:
                score -= 10
                recommendations.append(f"k-anonymity is {k} - consider increasing to 5+ for better protection")
        else:
            # No k-anonymity calculated
            if total_pii > 0:
                score -= 5
                recommendations.append("Configure quasi-identifiers to measure k-anonymity")

        # Re-identification risk
        reid = privacy_metrics.get("re_identification", {})
        overall_risk = reid.get("overall_risk", 0) if isinstance(reid, dict) else 0
        
        # Also check overall risk level
        overall = privacy_metrics.get("overall", {})
        if isinstance(overall, dict):
            risk_level = overall.get("risk_level", "").lower()
            if risk_level == "very high":
                score -= 25
                issues.append("Very high re-identification risk")
            elif risk_level == "high":
                score -= 15
                issues.append("High re-identification risk")
            elif risk_level == "medium":
                score -= 5

        if overall_risk > 0.5:
            score -= 20
            issues.append(f"Re-identification risk is {overall_risk:.0%}")
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
        total_pii = pii_summary.get("total_pii", 0)
        
        # Check for PHI-related PII types with dynamic scoring
        medical_pii_found = 0
        phi_types = ["US_SSN", "DATE_TIME", "LOCATION", "PHONE_NUMBER", "EMAIL_ADDRESS", "PERSON"]
        
        for pii_type, pii_info in by_type.items():
            if pii_type in phi_types or any(t in pii_type.upper() for t in ["MEDICAL", "HEALTH", "SSN", "DATE"]):
                count = pii_info.get("count", 0) if isinstance(pii_info, dict) else 0
                medical_pii_found += count
                if not anonymization_applied:
                    score -= min(10, count)  # Cap penalty per type
                    issues.append(f"{pii_type} detected ({count} instances)")

        # Safe Harbor method requires removal of 18 identifiers
        pii_type_count = len(by_type)
        if pii_type_count > 5:
            score -= min(15, pii_type_count * 2)
            recommendations.append(f"Multiple identifier types ({pii_type_count}) - consider Safe Harbor de-identification")

        # k-anonymity for HIPAA should be higher (5+)
        k_anon = privacy_metrics.get("k_anonymity", {})
        k = k_anon.get("k", 0) if isinstance(k_anon, dict) else 0
        
        if k > 0:
            if k < 3:
                score -= 25
                issues.append(f"k-anonymity is {k} (HIPAA requires higher protection)")
            elif k < 5:
                score -= 10
                recommendations.append(f"k-anonymity is {k} - increase to 5+ for HIPAA")
        elif total_pii > 0:
            score -= 5
            recommendations.append("Configure quasi-identifiers for k-anonymity measurement")

        # Check overall risk level
        overall = privacy_metrics.get("overall", {})
        if isinstance(overall, dict):
            risk_level = overall.get("risk_level", "").lower()
            if risk_level in ["very high", "high"]:
                score -= 15
                issues.append(f"{risk_level.title()} re-identification risk")

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

        total_pii = pii_summary.get("total_pii", 0)
        by_type = pii_summary.get("by_type", {})

        # Personal information detection - dynamic scoring
        if total_pii > 0:
            if not anonymization_applied:
                score -= 25
                issues.append(f"Personal information ({total_pii} instances) not de-identified")
                recommendations.append("De-identify personal information")
            else:
                # Even anonymized, check if high volume
                if total_pii > 100:
                    score -= 5
                    recommendations.append("High volume of personal data - ensure data minimization")

        # Check for high-risk PII types
        high_risk_types = ["US_SSN", "CREDIT_CARD", "FINANCIAL"]
        for pii_type in by_type.keys():
            if any(hr in pii_type.upper() for hr in high_risk_types):
                score -= 5
                issues.append(f"High-risk personal data detected: {pii_type}")

        # Check k-anonymity
        k_anon = privacy_metrics.get("k_anonymity", {})
        k = k_anon.get("k", 0) if isinstance(k_anon, dict) else 0
        
        if k > 0 and k < 3:
            score -= 15
            issues.append(f"k-anonymity of {k} increases re-identification risk")

        # Re-identification risk
        overall = privacy_metrics.get("overall", {})
        if isinstance(overall, dict):
            overall_risk = overall.get("overall_risk", 0)
            if overall_risk > 0.5:
                score -= 20
                issues.append(f"Re-identification risk above threshold ({overall_risk:.0%})")
                recommendations.append("Ensure data cannot be re-identified")
            elif overall_risk > 0.3:
                score -= 10
                recommendations.append("Consider additional de-identification measures")

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

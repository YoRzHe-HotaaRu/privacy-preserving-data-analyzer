"""Unit tests for risk assessment module."""

import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from risk_assessment import RiskCalculator, ComplianceChecker


class TestRiskCalculator:
    """Test risk calculation functionality."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up calculator for each test."""
        self.calculator = RiskCalculator()
    
    @pytest.fixture
    def sample_df(self):
        """Sample DataFrame for testing."""
        return pd.DataFrame({
            'age_range': ['20-30', '20-30', '30-40', '30-40', '30-40'],
            'gender': ['M', 'F', 'M', 'F', 'M'],
            'city': ['NYC', 'NYC', 'LA', 'LA', 'LA'],
            'salary': [50000, 55000, 60000, 65000, 70000]
        })
    
    def test_k_anonymity(self, sample_df):
        """Test k-anonymity calculation."""
        result = self.calculator.calculate_k_anonymity(
            sample_df, 
            quasi_identifiers=['age_range', 'gender']
        )
        
        assert 'k' in result
        assert result['k'] >= 1
        assert 'risk_level' in result
        assert 'recommendations' in result
    
    def test_k_anonymity_invalid_columns(self, sample_df):
        """Test k-anonymity with invalid columns."""
        result = self.calculator.calculate_k_anonymity(
            sample_df, 
            quasi_identifiers=['nonexistent_column']
        )
        
        assert 'error' in result
    
    def test_l_diversity(self, sample_df):
        """Test l-diversity calculation."""
        result = self.calculator.calculate_l_diversity(
            sample_df,
            quasi_identifiers=['age_range'],
            sensitive_attribute='salary'
        )
        
        assert 'l' in result
        assert result['l'] >= 1
        assert 'risk_level' in result
    
    def test_t_closeness(self, sample_df):
        """Test t-closeness calculation."""
        result = self.calculator.calculate_t_closeness(
            sample_df,
            quasi_identifiers=['age_range'],
            sensitive_attribute='city'
        )
        
        assert 't' in result
        assert 0 <= result['t'] <= 1
        assert 'risk_level' in result
    
    def test_re_identification_risk(self, sample_df):
        """Test re-identification risk calculation."""
        result = self.calculator.calculate_re_identification_risk(
            sample_df,
            quasi_identifiers=['age_range', 'gender', 'city']
        )
        
        assert 'sample_uniqueness' in result
        assert 'overall_risk' in result
        assert 'attack_model_risks' in result
        assert 'risk_level' in result
    
    def test_all_metrics(self, sample_df):
        """Test calculating all metrics."""
        result = self.calculator.calculate_all_metrics(
            sample_df,
            quasi_identifiers=['age_range', 'gender'],
            sensitive_attribute='salary'
        )
        
        assert 'k_anonymity' in result
        assert 'l_diversity' in result
        assert 't_closeness' in result
        assert 're_identification' in result
        assert 'overall' in result


class TestComplianceChecker:
    """Test compliance checking functionality."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up checker for each test."""
        self.checker = ComplianceChecker()
    
    @pytest.fixture
    def sample_privacy_metrics(self):
        """Sample privacy metrics."""
        return {
            'k_anonymity': {'k': 5},
            're_identification': {'overall_risk': 0.1}
        }
    
    @pytest.fixture
    def sample_pii_summary(self):
        """Sample PII summary."""
        return {
            'total_pii': 10,
            'by_type': {
                'EMAIL_ADDRESS': {'count': 5},
                'PHONE_NUMBER': {'count': 5}
            }
        }
    
    def test_check_gdpr(self, sample_privacy_metrics, sample_pii_summary):
        """Test GDPR compliance check."""
        result = self.checker.check_gdpr(
            sample_privacy_metrics,
            sample_pii_summary,
            anonymization_applied=True
        )
        
        assert result['regulation'] == 'GDPR'
        assert 'score' in result
        assert 'status' in result
        assert 'issues' in result
        assert 'recommendations' in result
    
    def test_check_hipaa(self, sample_privacy_metrics, sample_pii_summary):
        """Test HIPAA compliance check."""
        result = self.checker.check_hipaa(
            sample_privacy_metrics,
            sample_pii_summary,
            anonymization_applied=True
        )
        
        assert result['regulation'] == 'HIPAA'
        assert 0 <= result['score'] <= 100
    
    def test_check_ccpa(self, sample_privacy_metrics, sample_pii_summary):
        """Test CCPA compliance check."""
        result = self.checker.check_ccpa(
            sample_privacy_metrics,
            sample_pii_summary,
            anonymization_applied=True
        )
        
        assert result['regulation'] == 'CCPA'
        assert 0 <= result['score'] <= 100
    
    def test_check_all(self, sample_privacy_metrics, sample_pii_summary):
        """Test checking all regulations."""
        result = self.checker.check_all(
            sample_privacy_metrics,
            sample_pii_summary,
            anonymization_applied=True
        )
        
        assert 'gdpr' in result
        assert 'hipaa' in result
        assert 'ccpa' in result
        assert 'overall_compliant' in result
    
    def test_non_compliant_without_anonymization(self, sample_privacy_metrics, sample_pii_summary):
        """Test non-compliance when anonymization not applied."""
        result = self.checker.check_gdpr(
            sample_privacy_metrics,
            sample_pii_summary,
            anonymization_applied=False
        )
        
        # Score should be lower without anonymization
        assert result['score'] < 100
        assert len(result['issues']) > 0

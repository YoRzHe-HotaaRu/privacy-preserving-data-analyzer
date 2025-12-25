"""Unit tests for PII detection module."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pii_detection import PIIDetector


class TestPIIDetector:
    """Test PII detection functionality."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up detector for each test."""
        self.detector = PIIDetector()
    
    def test_detect_email(self, sample_text_with_pii):
        """Test email detection."""
        results = self.detector.detect("Contact me at john@example.com")
        
        assert len(results) >= 1
        email_results = [r for r in results if r['entity_type'] == 'EMAIL_ADDRESS']
        assert len(email_results) == 1
        assert 'john@example.com' in email_results[0]['text']
    
    def test_detect_phone(self):
        """Test phone number detection."""
        results = self.detector.detect("Call me at +1-555-123-4567")
        
        phone_results = [r for r in results if r['entity_type'] == 'PHONE_NUMBER']
        assert len(phone_results) >= 1
    
    def test_detect_ssn(self):
        """Test SSN detection."""
        results = self.detector.detect("SSN: 123-45-6789")
        
        ssn_results = [r for r in results if r['entity_type'] == 'US_SSN']
        assert len(ssn_results) >= 1
    
    def test_detect_credit_card(self):
        """Test credit card detection."""
        results = self.detector.detect("Card: 4111-1111-1111-1111")
        
        cc_results = [r for r in results if r['entity_type'] == 'CREDIT_CARD']
        assert len(cc_results) >= 1
    
    def test_no_pii(self, sample_text_without_pii):
        """Test text without PII."""
        results = self.detector.detect(sample_text_without_pii)
        
        # Should have minimal or no PII detected
        assert len(results) <= 1
    
    def test_empty_text(self):
        """Test empty text."""
        results = self.detector.detect("")
        assert results == []
    
    def test_none_text(self):
        """Test None input."""
        results = self.detector.detect(None)
        assert results == []
    
    def test_batch_detection(self):
        """Test batch PII detection."""
        texts = [
            "Email: john@test.com",
            "Phone: 555-123-4567",
            "No PII here"
        ]
        
        results = self.detector.detect_batch(texts)
        
        assert len(results) == 3
        assert len(results[0]) >= 1  # Email
        assert len(results[1]) >= 1  # Phone
    
    def test_pii_summary(self, sample_text_with_pii):
        """Test PII summary generation."""
        summary = self.detector.get_pii_summary(sample_text_with_pii)
        
        assert 'total_pii' in summary
        assert 'by_type' in summary
        assert summary['total_pii'] >= 1

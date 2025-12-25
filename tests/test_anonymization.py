"""Unit tests for anonymization module."""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from anonymization import DataAnonymizer
from anonymization.strategies import (
    Tokenizer,
    generalize,
    generalize_age,
    hash_value,
    mask,
    mask_email,
    mask_name,
    mask_phone,
    perturb,
    suppress,
)


class TestAnonymizationStrategies:
    """Test individual anonymization strategies."""

    def test_suppress(self):
        """Test suppression strategy."""
        result = suppress("John Smith", "PERSON")
        assert result == "[REDACTED]"

    def test_mask_email(self):
        """Test email masking."""
        result = mask_email("john@example.com")
        assert result == "j***@example.com"

        result = mask_email("ab@test.org")
        assert "@test.org" in result

    def test_mask_phone(self):
        """Test phone masking."""
        result = mask_phone("+1-555-123-4567")
        assert "4567" in result
        assert "***" in result

    def test_mask_name(self):
        """Test name masking."""
        result = mask_name("John Smith")
        assert result == "J*** S****"

    def test_generalize_age(self):
        """Test age generalization."""
        assert generalize_age("25") == "25-34"
        assert generalize_age("17") == "<18"
        assert generalize_age("65") == "65+"
        assert generalize_age("45") == "45-54"

    def test_perturb_numeric(self):
        """Test numeric perturbation."""
        result = perturb("100", noise_level=0.1)
        value = float(result)
        assert 50 <= value <= 150  # Within reasonable noise range

    def test_hash_value(self):
        """Test hashing."""
        result = hash_value("john@example.com")
        assert len(result) == 16
        assert result != "john@example.com"

        # Same input = same output
        result2 = hash_value("john@example.com")
        assert result == result2

    def test_hash_with_salt(self):
        """Test hashing with salt."""
        result1 = hash_value("john@example.com", salt="salt1")
        result2 = hash_value("john@example.com", salt="salt2")
        assert result1 != result2


class TestTokenizer:
    """Test tokenization strategy."""

    def test_tokenize(self):
        """Test tokenization."""
        tokenizer = Tokenizer()

        token1 = tokenizer.tokenize("john@example.com")
        assert token1.startswith("[TOKEN_")

        # Same value gets same token
        token2 = tokenizer.tokenize("john@example.com")
        assert token1 == token2

    def test_detokenize(self):
        """Test detokenization."""
        tokenizer = Tokenizer()

        token = tokenizer.tokenize("secret_value")
        result = tokenizer.detokenize(token)
        assert result == "secret_value"

    def test_get_mapping(self):
        """Test get mapping."""
        tokenizer = Tokenizer()
        tokenizer.tokenize("value1")
        tokenizer.tokenize("value2")

        mapping = tokenizer.get_mapping()
        assert len(mapping) == 2


class TestDataAnonymizer:
    """Test DataAnonymizer class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up anonymizer for each test."""
        self.anonymizer = DataAnonymizer()

    def test_apply_strategy_mask(self):
        """Test applying mask strategy."""
        result = self.anonymizer.apply_strategy("john@test.com", "EMAIL_ADDRESS", "mask")
        assert "***" in result
        assert "@test.com" in result

    def test_apply_strategy_suppress(self):
        """Test applying suppress strategy."""
        result = self.anonymizer.apply_strategy("123-45-6789", "US_SSN", "suppression")
        assert result == "[REDACTED]"

    def test_anonymize_dataframe(self, sample_dataframe):
        """Test DataFrame anonymization."""
        pii_columns = {"email": "EMAIL_ADDRESS", "phone": "PHONE_NUMBER"}

        result = self.anonymizer.anonymize_dataframe(sample_dataframe, pii_columns)

        # Original shouldn't be modified
        assert sample_dataframe["email"].iloc[0] == "john@email.com"

        # Result should be anonymized
        assert "***" in result["email"].iloc[0]
        assert "***" in result["phone"].iloc[0]

        # Non-PII columns unchanged
        assert result["name"].iloc[0] == "John Smith"

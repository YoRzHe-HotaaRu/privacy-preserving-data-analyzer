"""Pytest configuration and fixtures."""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


@pytest.fixture
def sample_dataframe():
    """Sample DataFrame with PII for testing."""
    return pd.DataFrame({
        'name': ['John Smith', 'Jane Doe', 'Bob Wilson'],
        'email': ['john@email.com', 'jane@company.org', 'bob@test.com'],
        'phone': ['+1-555-123-4567', '+1-555-234-5678', '+1-555-345-6789'],
        'age': [32, 28, 45],
        'salary': [75000, 82000, 95000],
        'city': ['New York', 'San Francisco', 'Chicago']
    })


@pytest.fixture
def sample_text_with_pii():
    """Sample text containing PII."""
    return "Contact John Smith at john@email.com or call +1-555-123-4567."


@pytest.fixture
def sample_text_without_pii():
    """Sample text without PII."""
    return "This is a simple text about data analysis and privacy."


@pytest.fixture
def numeric_data():
    """Sample numeric data for DP testing."""
    return [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

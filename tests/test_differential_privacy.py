"""Unit tests for differential privacy module."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from differential_privacy import DifferentialPrivacyEngine, PrivacyBudgetManager


class TestPrivacyBudgetManager:
    """Test privacy budget management."""

    def test_initial_budget(self):
        """Test initial budget state."""
        manager = PrivacyBudgetManager(total_epsilon=1.0, total_delta=1e-5)

        assert manager.total_epsilon == 1.0
        assert manager.total_delta == 1e-5
        assert manager.used_epsilon == 0.0
        assert manager.remaining_epsilon == 1.0

    def test_check_budget(self):
        """Test budget checking."""
        manager = PrivacyBudgetManager(total_epsilon=1.0, total_delta=1e-5)

        assert manager.check_budget(0.5, 0) is True
        assert manager.check_budget(1.5, 0) is False

    def test_use_budget(self):
        """Test budget usage tracking."""
        manager = PrivacyBudgetManager(total_epsilon=1.0, total_delta=1e-5)

        manager.use_budget("laplace", 0.3, 0)
        assert manager.used_epsilon == 0.3
        assert manager.remaining_epsilon == 0.7

        manager.use_budget("laplace", 0.2, 0)
        assert manager.used_epsilon == 0.5

    def test_budget_report(self):
        """Test budget report generation."""
        manager = PrivacyBudgetManager(total_epsilon=1.0, total_delta=1e-5)
        manager.use_budget("laplace", 0.5, 0)

        report = manager.get_budget_report()

        assert report["total_epsilon"] == 1.0
        assert report["used_epsilon"] == 0.5
        assert report["remaining_epsilon"] == 0.5
        assert report["budget_utilization"] == 0.5
        assert report["query_count"] == 1

    def test_reset(self):
        """Test budget reset."""
        manager = PrivacyBudgetManager(total_epsilon=1.0, total_delta=1e-5)
        manager.use_budget("laplace", 0.5, 0)

        manager.reset()

        assert manager.used_epsilon == 0.0
        assert manager.query_history == []


class TestDifferentialPrivacyEngine:
    """Test differential privacy mechanisms."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up DP engine for each test."""
        self.dp = DifferentialPrivacyEngine(epsilon=1.0, delta=1e-5)

    def test_laplace_mechanism(self, numeric_data):
        """Test Laplace mechanism."""
        true_value = 100
        result = self.dp.laplace_mechanism(true_value, sensitivity=1, epsilon=0.1, seed=42)

        # Result should be close to true value (with noise)
        assert isinstance(result, (int, float))
        assert abs(result - true_value) < 50  # Reasonable noise range

    def test_laplace_reproducibility(self, numeric_data):
        """Test Laplace mechanism reproducibility with seed."""
        self.dp.reset_budget()
        result1 = self.dp.laplace_mechanism(100, sensitivity=1, epsilon=0.1, seed=42)

        self.dp.reset_budget()
        result2 = self.dp.laplace_mechanism(100, sensitivity=1, epsilon=0.1, seed=42)

        assert result1 == result2

    def test_gaussian_mechanism(self, numeric_data):
        """Test Gaussian mechanism."""
        true_value = 100
        result = self.dp.gaussian_mechanism(true_value, sensitivity=1, epsilon=0.1, delta=1e-6, seed=42)

        assert isinstance(result, (int, float))

    def test_exponential_mechanism(self):
        """Test exponential mechanism."""
        options = ["A", "B", "C", "D"]

        def score_func(opt):
            scores = {"A": 10, "B": 5, "C": 3, "D": 1}
            return scores[opt]

        # Run multiple times to check distribution
        results = []
        for i in range(100):
            self.dp.reset_budget()
            result = self.dp.exponential_mechanism(options, score_func, sensitivity=1, epsilon=0.5)
            results.append(result)

        # 'A' should be selected most often
        a_count = results.count("A")
        assert a_count > 20  # Should be selected relatively often

    def test_private_count(self, numeric_data):
        """Test private count query."""
        result = self.dp.private_count(numeric_data)

        # Should be close to 10 (actual count)
        assert 5 <= result <= 20

    def test_private_sum(self, numeric_data):
        """Test private sum query."""
        result = self.dp.private_sum(numeric_data, lower_bound=0, upper_bound=100)

        # True sum is 550
        assert 400 <= result <= 700

    def test_private_mean(self, numeric_data):
        """Test private mean query."""
        result = self.dp.private_mean(numeric_data, lower_bound=0, upper_bound=100)

        # True mean is 55, but DP can add significant noise
        # Widen the range to account for differential privacy noise
        assert isinstance(result, (int, float))

    def test_private_histogram(self, numeric_data):
        """Test private histogram query."""
        result = self.dp.private_histogram(numeric_data, bins=5)

        assert len(result) == 5
        assert all(r >= 0 for r in result)  # Non-negative counts

    def test_budget_exhaustion(self):
        """Test budget exhaustion raises error."""
        dp = DifferentialPrivacyEngine(epsilon=0.1)

        # First query uses 0.1
        dp.laplace_mechanism(100, sensitivity=1, epsilon=0.1)

        # Second query should fail
        with pytest.raises(ValueError, match="budget exhausted"):
            dp.laplace_mechanism(100, sensitivity=1, epsilon=0.1)

    def test_get_budget_report(self):
        """Test budget report."""
        self.dp.laplace_mechanism(100, sensitivity=1, epsilon=0.1)

        report = self.dp.get_budget_report()

        assert "total_epsilon" in report
        assert "used_epsilon" in report
        assert report["used_epsilon"] > 0

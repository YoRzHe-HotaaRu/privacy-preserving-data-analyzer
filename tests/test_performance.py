"""Performance and benchmark tests."""

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from anonymization import DataAnonymizer
from differential_privacy import DifferentialPrivacyEngine
from pii_detection import PIIDetector


class TestPerformance:
    """Performance benchmark tests."""

    @pytest.fixture
    def large_dataframe(self):
        """Create large DataFrame for stress testing."""
        np.random.seed(42)
        n_rows = 10000

        names = [f"User{i}" for i in range(n_rows)]
        emails = [f"user{i}@company.com" for i in range(n_rows)]
        phones = [f"+1-555-{i:07d}" for i in range(n_rows)]
        ages = np.random.randint(18, 80, n_rows)
        salaries = np.random.randint(30000, 200000, n_rows)

        return pd.DataFrame({"name": names, "email": emails, "phone": phones, "age": ages, "salary": salaries})

    @pytest.fixture
    def detector(self):
        return PIIDetector()

    @pytest.fixture
    def anonymizer(self):
        return DataAnonymizer()

    @pytest.fixture
    def dp_engine(self):
        return DifferentialPrivacyEngine(epsilon=1.0)

    # ==================== PII Detection Benchmarks ====================

    def test_pii_detection_single_text(self, detector, benchmark):
        """Benchmark: Single PII detection."""
        text = "Contact John Smith at john@email.com or call +1-555-123-4567"

        result = benchmark(detector.detect, text)
        assert len(result) >= 1

    def test_pii_detection_batch_100(self, detector, benchmark):
        """Benchmark: Batch PII detection (100 texts)."""
        texts = [f"Email user{i}@test.com" for i in range(100)]

        result = benchmark(detector.detect_batch, texts)
        assert len(result) == 100

    def test_pii_detection_batch_1000(self, detector, benchmark):
        """Benchmark: Batch PII detection (1000 texts)."""
        texts = [f"Email user{i}@test.com" for i in range(1000)]

        result = benchmark(detector.detect_batch, texts)
        assert len(result) == 1000

    # ==================== Anonymization Benchmarks ====================

    def test_anonymize_dataframe_small(self, anonymizer, benchmark):
        """Benchmark: DataFrame anonymization (100 rows)."""
        df = pd.DataFrame(
            {"email": [f"user{i}@test.com" for i in range(100)], "phone": [f"+1-555-{i:07d}" for i in range(100)]}
        )
        pii_columns = {"email": "EMAIL_ADDRESS", "phone": "PHONE_NUMBER"}

        result = benchmark(anonymizer.anonymize_dataframe, df, pii_columns)
        assert len(result) == 100

    def test_anonymize_dataframe_large(self, anonymizer, large_dataframe, benchmark):
        """Benchmark: DataFrame anonymization (10K rows)."""
        pii_columns = {"email": "EMAIL_ADDRESS", "phone": "PHONE_NUMBER", "name": "PERSON"}

        result = benchmark(anonymizer.anonymize_dataframe, large_dataframe, pii_columns)
        assert len(result) == 10000

    # ==================== Differential Privacy Benchmarks ====================

    def test_laplace_mechanism_single(self, dp_engine, benchmark):
        """Benchmark: Laplace mechanism (single value)."""
        dp_engine.reset_budget()

        def run():
            dp_engine.reset_budget()
            return dp_engine.laplace_mechanism(100, sensitivity=1, epsilon=0.1)

        result = benchmark(run)
        assert isinstance(result, (int, float))

    def test_private_mean_large_dataset(self, dp_engine, benchmark):
        """Benchmark: Private mean on large dataset."""
        data = np.random.normal(50, 10, 10000)

        def run():
            dp_engine.reset_budget()
            return dp_engine.private_mean(data, lower_bound=0, upper_bound=100)

        result = benchmark(run)
        assert 30 <= result <= 70

    def test_private_histogram_large(self, dp_engine, benchmark):
        """Benchmark: Private histogram (10K values, 50 bins)."""
        data = np.random.normal(50, 15, 10000)

        def run():
            dp_engine.reset_budget()
            return dp_engine.private_histogram(data, bins=50)

        result = benchmark(run)
        assert len(result) == 50

    # ==================== Memory Tests ====================

    def test_memory_usage_large_anonymization(self, anonymizer, large_dataframe):
        """Test memory efficiency for large dataset."""
        import tracemalloc

        tracemalloc.start()

        pii_columns = {"email": "EMAIL_ADDRESS", "phone": "PHONE_NUMBER"}
        result = anonymizer.anonymize_dataframe(large_dataframe, pii_columns)

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Peak memory should be reasonable (<500MB for 10K rows)
        peak_mb = peak / 1024 / 1024
        assert peak_mb < 500, f"Peak memory usage too high: {peak_mb:.2f} MB"

        print(f"\nMemory usage - Current: {current/1024/1024:.2f} MB, Peak: {peak_mb:.2f} MB")

    # ==================== Latency Tests ====================

    def test_api_latency_simulation(self, detector, anonymizer):
        """Test end-to-end latency for typical API request."""
        # Simulate typical API request: detect + anonymize
        df = pd.DataFrame(
            {"email": [f"user{i}@test.com" for i in range(100)], "data": [f"Data for user{i}" for i in range(100)]}
        )

        start = time.time()

        # Detect PII in sample
        for _, row in df.head(10).iterrows():
            detector.detect(str(row["email"]))

        # Anonymize
        pii_columns = {"email": "EMAIL_ADDRESS"}
        anonymizer.anonymize_dataframe(df, pii_columns)

        elapsed = time.time() - start

        # Should complete in <2 seconds
        assert elapsed < 2.0, f"API latency too high: {elapsed:.2f}s"
        print(f"\nEnd-to-end latency: {elapsed*1000:.2f} ms")


class TestStress:
    """Stress tests for edge cases."""

    def test_very_long_text(self):
        """Test PII detection on very long text."""
        detector = PIIDetector()

        # Create 10KB text
        long_text = "Email: test@example.com. " * 500

        start = time.time()
        results = detector.detect(long_text)
        elapsed = time.time() - start

        assert elapsed < 5.0, f"Long text processing too slow: {elapsed:.2f}s"
        assert len(results) >= 1

    def test_many_pii_instances(self):
        """Test detection with many PII instances."""
        detector = PIIDetector()

        # Text with 100 email addresses
        text = " ".join([f"user{i}@domain{i}.com" for i in range(100)])

        start = time.time()
        results = detector.detect(text)
        elapsed = time.time() - start

        assert elapsed < 5.0
        assert len(results) >= 50  # Should detect most of them

    def test_concurrent_budget_tracking(self):
        """Test privacy budget tracking under many queries."""
        dp = DifferentialPrivacyEngine(epsilon=10.0, delta=1e-3)

        query_count = 0
        total_epsilon_used = 0

        try:
            for i in range(100):
                dp.private_count([1, 2, 3, 4, 5])
                query_count += 1
        except ValueError:
            pass  # Budget exhausted

        report = dp.get_budget_report()
        print(f"\nQueries before exhaustion: {query_count}")
        print(f"Budget used: {report['used_epsilon']:.2f}/{report['total_epsilon']}")

        assert report["used_epsilon"] <= report["total_epsilon"]

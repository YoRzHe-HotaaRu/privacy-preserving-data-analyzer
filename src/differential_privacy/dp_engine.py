"""Differential Privacy Module - Main DP Engine"""

from typing import Any, Callable, List, Optional, Union

import numpy as np

from .budget_manager import PrivacyBudgetManager


class DifferentialPrivacyEngine:
    """Complete differential privacy engine with all mechanisms."""

    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        """
        Initialize DP engine.

        Args:
            epsilon: Privacy budget
            delta: Failure probability
        """
        self.epsilon = epsilon
        self.delta = delta
        self.budget_manager = PrivacyBudgetManager(epsilon, delta)

    def laplace_mechanism(
        self, true_value: Union[float, np.ndarray], sensitivity: float, epsilon: float = None, seed: int = None
    ) -> Union[float, np.ndarray]:
        """
        Add Laplace noise for ε-differential privacy.

        Args:
            true_value: True query result
            sensitivity: Query sensitivity
            epsilon: Privacy parameter (uses budget if None)
            seed: Random seed for reproducibility

        Returns:
            Noisy result
        """
        if epsilon is None:
            epsilon = min(0.1, self.budget_manager.remaining_epsilon / 10)

        if not self.budget_manager.check_budget(epsilon, 0):
            raise ValueError("Privacy budget exhausted")

        if seed is not None:
            np.random.seed(seed)

        scale = sensitivity / epsilon

        if isinstance(true_value, np.ndarray):
            noise = np.random.laplace(0, scale, size=true_value.shape)
        else:
            noise = np.random.laplace(0, scale)

        private_value = true_value + noise

        self.budget_manager.use_budget("laplace", epsilon, 0, {"sensitivity": sensitivity, "scale": scale})

        return private_value

    def gaussian_mechanism(
        self,
        true_value: Union[float, np.ndarray],
        sensitivity: float,
        epsilon: float = None,
        delta: float = None,
        seed: int = None,
    ) -> Union[float, np.ndarray]:
        """
        Add Gaussian noise for (ε, δ)-differential privacy.

        Args:
            true_value: True query result
            sensitivity: Query sensitivity
            epsilon: Privacy parameter
            delta: Failure probability
            seed: Random seed

        Returns:
            Noisy result
        """
        if epsilon is None:
            epsilon = min(0.1, self.budget_manager.remaining_epsilon / 10)
        if delta is None:
            delta = min(1e-6, self.budget_manager.remaining_delta / 10)

        if not self.budget_manager.check_budget(epsilon, delta):
            raise ValueError("Privacy budget exhausted")

        if seed is not None:
            np.random.seed(seed)

        sigma = np.sqrt(2 * np.log(1.25 / delta)) * sensitivity / epsilon

        if isinstance(true_value, np.ndarray):
            noise = np.random.normal(0, sigma, size=true_value.shape)
        else:
            noise = np.random.normal(0, sigma)

        private_value = true_value + noise

        self.budget_manager.use_budget("gaussian", epsilon, delta, {"sensitivity": sensitivity, "sigma": sigma})

        return private_value

    def exponential_mechanism(
        self,
        options: List[Any],
        scoring_function: Callable,
        sensitivity: float,
        epsilon: float = None,
        seed: int = None,
    ) -> Any:
        """
        Select option using exponential mechanism.

        Args:
            options: List of possible options
            scoring_function: Function to score each option
            sensitivity: Sensitivity of scoring function
            epsilon: Privacy parameter
            seed: Random seed

        Returns:
            Selected option
        """
        if epsilon is None:
            epsilon = min(0.1, self.budget_manager.remaining_epsilon / 10)

        if not self.budget_manager.check_budget(epsilon, 0):
            raise ValueError("Privacy budget exhausted")

        if seed is not None:
            np.random.seed(seed)

        scores = np.array([scoring_function(opt) for opt in options])
        max_score = np.max(scores)

        # Numerical stability: subtract max score
        scaled_scores = (epsilon * (scores - max_score)) / (2 * sensitivity)
        exp_scores = np.exp(scaled_scores)
        probabilities = exp_scores / np.sum(exp_scores)

        selected_idx = np.random.choice(len(options), p=probabilities)
        selected_option = options[selected_idx]

        self.budget_manager.use_budget(
            "exponential", epsilon, 0, {"num_options": len(options), "sensitivity": sensitivity}
        )

        return selected_option

    # ==================== High-Level Query Interface ====================

    def private_count(self, data: Union[List, np.ndarray], epsilon: float = None) -> float:
        """Private count query."""
        true_count = len(data)
        sensitivity = 1
        return self.laplace_mechanism(true_count, sensitivity, epsilon)

    def private_sum(
        self, data: Union[List[float], np.ndarray], lower_bound: float, upper_bound: float, epsilon: float = None
    ) -> float:
        """Private sum query with bounded data."""
        # Clip data to bounds
        clipped = np.clip(data, lower_bound, upper_bound)
        true_sum = np.sum(clipped)
        sensitivity = upper_bound - lower_bound
        return self.laplace_mechanism(true_sum, sensitivity, epsilon)

    def private_mean(
        self, data: Union[List[float], np.ndarray], lower_bound: float, upper_bound: float, epsilon: float = None
    ) -> float:
        """Private mean query with bounded data."""
        if len(data) == 0:
            return 0.0
        clipped = np.clip(data, lower_bound, upper_bound)
        true_mean = np.mean(clipped)
        sensitivity = (upper_bound - lower_bound) / len(data)
        return self.laplace_mechanism(true_mean, sensitivity, epsilon)

    def private_histogram(
        self, data: Union[List, np.ndarray], bins: Union[int, List] = 10, epsilon: float = None
    ) -> np.ndarray:
        """
        Private histogram query.

        Each bin count has sensitivity 1 (one person can only be in one bin).
        """
        counts, _ = np.histogram(data, bins=bins)
        sensitivity = 1

        # Add noise to each bin
        private_counts = []
        remaining_eps = epsilon if epsilon else self.budget_manager.remaining_epsilon
        eps_per_bin = remaining_eps / len(counts)

        for count in counts:
            noisy = self.laplace_mechanism(float(count), sensitivity, eps_per_bin)
            private_counts.append(max(0, noisy))  # Ensure non-negative

        return np.array(private_counts)

    def private_percentile(
        self,
        data: Union[List[float], np.ndarray],
        percentile: float,
        lower_bound: float,
        upper_bound: float,
        epsilon: float = None,
    ) -> float:
        """Private percentile query."""
        clipped = np.clip(data, lower_bound, upper_bound)
        true_percentile = np.percentile(clipped, percentile)
        # Sensitivity based on data range
        sensitivity = (upper_bound - lower_bound) / 2
        return self.laplace_mechanism(true_percentile, sensitivity, epsilon)

    def private_variance(
        self, data: Union[List[float], np.ndarray], lower_bound: float, upper_bound: float, epsilon: float = None
    ) -> float:
        """Private variance query."""
        if len(data) <= 1:
            return 0.0
        clipped = np.clip(data, lower_bound, upper_bound)
        true_var = np.var(clipped)
        sensitivity = ((upper_bound - lower_bound) ** 2) / len(data)
        return max(0, self.laplace_mechanism(true_var, sensitivity, epsilon))

    # ==================== Budget Management ====================

    def get_budget_report(self) -> dict:
        """Get privacy budget report."""
        return self.budget_manager.get_budget_report()

    def reset_budget(self):
        """Reset privacy budget (use with caution)."""
        self.budget_manager.reset()

    def check_budget(self, epsilon: float = 0.1, delta: float = 0) -> bool:
        """Check if budget allows a query."""
        return self.budget_manager.check_budget(epsilon, delta)

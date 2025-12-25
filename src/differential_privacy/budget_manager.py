"""Differential Privacy Module - Privacy Budget Manager"""

from typing import Dict, Any, List
from datetime import datetime


class PrivacyBudgetManager:
    """Manage privacy budget for differential privacy queries."""
    
    def __init__(self, total_epsilon: float = 1.0, total_delta: float = 1e-5):
        """
        Initialize budget manager.
        
        Args:
            total_epsilon: Total privacy budget
            total_delta: Total delta parameter
        """
        self.total_epsilon = total_epsilon
        self.total_delta = total_delta
        self.used_epsilon = 0.0
        self.used_delta = 0.0
        self.query_history: List[Dict[str, Any]] = []
    
    @property
    def remaining_epsilon(self) -> float:
        """Get remaining epsilon budget."""
        return max(0, self.total_epsilon - self.used_epsilon)
    
    @property
    def remaining_delta(self) -> float:
        """Get remaining delta budget."""
        return max(0, self.total_delta - self.used_delta)
    
    def check_budget(self, epsilon: float, delta: float = 0) -> bool:
        """
        Check if there is sufficient budget for a query.
        
        Args:
            epsilon: Required epsilon
            delta: Required delta
        
        Returns:
            True if budget is available
        """
        return (self.used_epsilon + epsilon <= self.total_epsilon and 
                self.used_delta + delta <= self.total_delta)
    
    def use_budget(self, query_type: str, epsilon: float, delta: float = 0, 
                 metadata: Dict[str, Any] = None):
        """
        Record budget usage for a query.
        
        Args:
            query_type: Type of query (laplace, gaussian, exponential)
            epsilon: Epsilon used
            delta: Delta used
            metadata: Additional query metadata
        """
        self.used_epsilon += epsilon
        self.used_delta += delta
        
        self.query_history.append({
            'timestamp': datetime.now().isoformat(),
            'query_type': query_type,
            'epsilon': epsilon,
            'delta': delta,
            'cumulative_epsilon': self.used_epsilon,
            'cumulative_delta': self.used_delta,
            'metadata': metadata or {}
        })
    
    def get_budget_report(self) -> Dict[str, Any]:
        """Get comprehensive budget report."""
        return {
            'total_epsilon': self.total_epsilon,
            'total_delta': self.total_delta,
            'used_epsilon': self.used_epsilon,
            'used_delta': self.used_delta,
            'remaining_epsilon': self.remaining_epsilon,
            'remaining_delta': self.remaining_delta,
            'budget_utilization': self.used_epsilon / self.total_epsilon if self.total_epsilon > 0 else 0,
            'query_count': len(self.query_history),
            'is_exhausted': self.used_epsilon >= self.total_epsilon,
            'warning': self._get_warning_status()
        }
    
    def _get_warning_status(self) -> str:
        """Get warning status based on budget utilization."""
        utilization = self.used_epsilon / self.total_epsilon if self.total_epsilon > 0 else 0
        
        if utilization >= 1.0:
            return 'EXHAUSTED'
        elif utilization >= 0.9:
            return 'CRITICAL'
        elif utilization >= 0.75:
            return 'WARNING'
        elif utilization >= 0.5:
            return 'MODERATE'
        else:
            return 'OK'
    
    def reset(self):
        """Reset the budget (use with caution)."""
        self.used_epsilon = 0.0
        self.used_delta = 0.0
        self.query_history = []
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get query history."""
        return list(self.query_history)

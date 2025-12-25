"""Risk Assessment Module - Risk Calculator"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional


class RiskCalculator:
    """Calculate privacy risk metrics."""
    
    def calculate_k_anonymity(self, df: pd.DataFrame, 
                            quasi_identifiers: List[str]) -> Dict[str, Any]:
        """
        Calculate k-anonymity for a DataFrame.
        
        k-anonymity ensures each record is indistinguishable from at least
        k-1 other records based on quasi-identifiers.
        
        Args:
            df: DataFrame to analyze
            quasi_identifiers: List of quasi-identifier columns
        
        Returns:
            Dictionary with k-anonymity analysis
        """
        if not quasi_identifiers or not all(col in df.columns for col in quasi_identifiers):
            return {'error': 'Invalid quasi-identifiers'}
        
        # Group by quasi-identifiers
        groups = df.groupby(quasi_identifiers).size()
        
        # Minimum k
        k = groups.min()
        
        # Distribution of group sizes
        distribution = groups.value_counts().sort_index().to_dict()
        
        # Find violating groups (groups with only 1 member are most at risk)
        violating = groups[groups < 5].reset_index(name='count')
        
        return {
            'k': int(k),
            'mean_group_size': float(groups.mean()),
            'median_group_size': float(groups.median()),
            'total_groups': len(groups),
            'distribution': distribution,
            'violating_groups_count': len(violating),
            'risk_level': self._get_k_risk_level(k),
            'recommendations': self._get_k_recommendations(k)
        }
    
    def calculate_l_diversity(self, df: pd.DataFrame,
                            quasi_identifiers: List[str],
                            sensitive_attribute: str) -> Dict[str, Any]:
        """
        Calculate l-diversity for a DataFrame.
        
        l-diversity ensures each equivalence class has at least l 
        well-represented values for the sensitive attribute.
        
        Args:
            df: DataFrame to analyze
            quasi_identifiers: List of quasi-identifier columns
            sensitive_attribute: Column containing sensitive data
        
        Returns:
            Dictionary with l-diversity analysis
        """
        if sensitive_attribute not in df.columns:
            return {'error': f'Sensitive attribute {sensitive_attribute} not found'}
        
        # Calculate diversity for each equivalence class
        groups = df.groupby(quasi_identifiers)[sensitive_attribute].apply(
            lambda x: x.nunique()
        )
        
        # Minimum l
        l = groups.min()
        
        # Violating groups
        violating = groups[groups < 3]
        
        return {
            'l': int(l),
            'mean_diversity': float(groups.mean()),
            'median_diversity': float(groups.median()),
            'violating_groups_count': len(violating),
            'risk_level': self._get_l_risk_level(l),
            'recommendations': self._get_l_recommendations(l)
        }
    
    def calculate_t_closeness(self, df: pd.DataFrame,
                             quasi_identifiers: List[str],
                             sensitive_attribute: str) -> Dict[str, Any]:
        """
        Calculate t-closeness for a DataFrame.
        
        t-closeness ensures the distribution of sensitive attribute in each
        equivalence class is close to the overall distribution.
        
        Args:
            df: DataFrame to analyze
            quasi_identifiers: List of quasi-identifier columns
            sensitive_attribute: Column containing sensitive data
        
        Returns:
            Dictionary with t-closeness analysis
        """
        if sensitive_attribute not in df.columns:
            return {'error': f'Sensitive attribute {sensitive_attribute} not found'}
        
        # Overall distribution
        overall_dist = df[sensitive_attribute].value_counts(normalize=True)
        
        # Calculate EMD for each equivalence class
        def calculate_emd(group):
            group_dist = group.value_counts(normalize=True)
            # Simple EMD approximation using L1 distance
            all_values = set(overall_dist.index) | set(group_dist.index)
            emd = 0
            for val in all_values:
                p = overall_dist.get(val, 0)
                q = group_dist.get(val, 0)
                emd += abs(p - q)
            return emd / 2  # Normalize
        
        groups = df.groupby(quasi_identifiers)[sensitive_attribute].apply(calculate_emd)
        
        # Maximum t (worst case)
        t = groups.max()
        
        return {
            't': float(t),
            'mean_distance': float(groups.mean()),
            'median_distance': float(groups.median()),
            'max_distance_group': str(groups.idxmax()) if len(groups) > 0 else None,
            'risk_level': self._get_t_risk_level(t),
            'recommendations': self._get_t_recommendations(t)
        }
    
    def calculate_re_identification_risk(self, df: pd.DataFrame,
                                        quasi_identifiers: List[str],
                                        population_size: int = None) -> Dict[str, Any]:
        """
        Calculate re-identification risk.
        
        Args:
            df: DataFrame to analyze
            quasi_identifiers: List of quasi-identifier columns
            population_size: Estimated population size
        
        Returns:
            Dictionary with risk metrics
        """
        # Group sizes
        groups = df.groupby(quasi_identifiers).size()
        
        # Sample uniqueness
        unique_records = (groups == 1).sum()
        sample_uniqueness = unique_records / len(df) if len(df) > 0 else 0
        
        # Population uniqueness estimate
        if population_size and population_size > len(df):
            # Simple estimate based on sample
            pop_uniqueness = sample_uniqueness * (len(df) / population_size)
        else:
            pop_uniqueness = sample_uniqueness
        
        # Attack model risks
        marketer_risk = sample_uniqueness  # Average re-id probability
        journalist_risk = 1 / groups.min() if groups.min() > 0 else 1  # Worst case
        prosecutor_risk = 1 / groups.max() if groups.max() > 0 else 1  # Best case for attacker
        
        # Overall risk
        overall_risk = (marketer_risk + journalist_risk) / 2
        
        return {
            'sample_uniqueness': float(sample_uniqueness),
            'population_uniqueness': float(pop_uniqueness),
            'unique_records': int(unique_records),
            'total_records': len(df),
            'attack_model_risks': {
                'marketer': float(marketer_risk),
                'journalist': float(journalist_risk),
                'prosecutor': float(prosecutor_risk)
            },
            'overall_risk': float(overall_risk),
            'risk_level': self._classify_risk(overall_risk),
            'recommendations': self._get_risk_recommendations(overall_risk)
        }
    
    def calculate_all_metrics(self, df: pd.DataFrame,
                            quasi_identifiers: List[str],
                            sensitive_attribute: str = None,
                            population_size: int = None) -> Dict[str, Any]:
        """
        Calculate all privacy metrics.
        
        Args:
            df: DataFrame to analyze
            quasi_identifiers: List of quasi-identifier columns
            sensitive_attribute: Column containing sensitive data
            population_size: Estimated population size
        
        Returns:
            Dictionary with all risk metrics
        """
        results = {}
        
        # k-anonymity
        results['k_anonymity'] = self.calculate_k_anonymity(df, quasi_identifiers)
        
        # l-diversity (if sensitive attribute provided)
        if sensitive_attribute:
            results['l_diversity'] = self.calculate_l_diversity(
                df, quasi_identifiers, sensitive_attribute
            )
            results['t_closeness'] = self.calculate_t_closeness(
                df, quasi_identifiers, sensitive_attribute
            )
        
        # Re-identification risk
        results['re_identification'] = self.calculate_re_identification_risk(
            df, quasi_identifiers, population_size
        )
        
        # Overall assessment
        results['overall'] = self._assess_overall(results)
        
        return results
    
    def _assess_overall(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall risk level."""
        risk_scores = []
        
        if 'k_anonymity' in results and 'k' in results['k_anonymity']:
            k = results['k_anonymity']['k']
            risk_scores.append((5 - min(k, 5)) / 5)
        
        if 're_identification' in results:
            risk_scores.append(results['re_identification']['overall_risk'])
        
        overall_risk = np.mean(risk_scores) if risk_scores else 0.5
        
        return {
            'overall_risk': float(overall_risk),
            'risk_level': self._classify_risk(overall_risk),
            'recommendations': self._get_risk_recommendations(overall_risk)
        }
    
    def _classify_risk(self, risk: float) -> str:
        """Classify risk level."""
        if risk < 0.1:
            return 'Very Low'
        elif risk < 0.3:
            return 'Low'
        elif risk < 0.5:
            return 'Medium'
        elif risk < 0.7:
            return 'High'
        else:
            return 'Very High'
    
    def _get_k_risk_level(self, k: int) -> str:
        if k >= 10:
            return 'Very Low'
        elif k >= 5:
            return 'Low'
        elif k >= 3:
            return 'Medium'
        elif k >= 2:
            return 'High'
        else:
            return 'Very High'
    
    def _get_l_risk_level(self, l: int) -> str:
        if l >= 5:
            return 'Very Low'
        elif l >= 3:
            return 'Low'
        elif l >= 2:
            return 'Medium'
        else:
            return 'High'
    
    def _get_t_risk_level(self, t: float) -> str:
        if t <= 0.1:
            return 'Very Low'
        elif t <= 0.2:
            return 'Low'
        elif t <= 0.3:
            return 'Medium'
        else:
            return 'High'
    
    def _get_k_recommendations(self, k: int) -> List[str]:
        if k >= 5:
            return ['k-anonymity level is acceptable']
        return [
            'Increase k-anonymity by generalizing quasi-identifiers',
            'Consider suppressing records in small groups',
            'Add more noise to near-unique records'
        ]
    
    def _get_l_recommendations(self, l: int) -> List[str]:
        if l >= 3:
            return ['l-diversity level is acceptable']
        return [
            'Increase diversity of sensitive attributes in groups',
            'Consider further anonymization of quasi-identifiers',
            'Apply noise to sensitive attribute values'
        ]
    
    def _get_t_recommendations(self, t: float) -> List[str]:
        if t <= 0.2:
            return ['t-closeness level is acceptable']
        return [
            'Distribution of sensitive attribute varies too much between groups',
            'Consider stronger anonymization',
            'Apply differential privacy to sensitive queries'
        ]
    
    def _get_risk_recommendations(self, risk: float) -> List[str]:
        if risk < 0.1:
            return ['Risk level is acceptable for most use cases']
        elif risk < 0.3:
            return ['Monitor risk levels regularly', 'Consider additional anonymization']
        elif risk < 0.5:
            return ['Apply stronger anonymization', 'Increase k-anonymity threshold']
        elif risk < 0.7:
            return ['URGENT: Risk level is high', 'Apply maximum anonymization', 'Consider not releasing data']
        else:
            return ['CRITICAL: Data should not be released', 'Apply all available privacy techniques']

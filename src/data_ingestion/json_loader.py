"""Data Ingestion Module - JSON Loader"""

import json
import pandas as pd
from typing import Dict, Any, Union
from pathlib import Path

from .base_loader import DataLoader


class JSONLoader(DataLoader):
    """Load data from JSON files."""
    
    def load(self, source: str, **kwargs) -> pd.DataFrame:
        """
        Load JSON file.
        
        Args:
            source: Path to JSON file
            **kwargs: Additional parameters
        
        Returns:
            DataFrame with loaded data
        """
        encoding = kwargs.get('encoding', 'utf-8')
        
        # Read JSON
        with open(source, 'r', encoding=encoding) as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, list):
            # Array of objects
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # Check for common structures
            if 'data' in data and isinstance(data['data'], list):
                df = pd.DataFrame(data['data'])
            elif 'records' in data and isinstance(data['records'], list):
                df = pd.DataFrame(data['records'])
            elif 'results' in data and isinstance(data['results'], list):
                df = pd.DataFrame(data['results'])
            elif 'items' in data and isinstance(data['items'], list):
                df = pd.DataFrame(data['items'])
            elif 'rows' in data and isinstance(data['rows'], list):
                df = pd.DataFrame(data['rows'])
            else:
                # Treat as single record or try to normalize
                try:
                    df = pd.json_normalize(data)
                except Exception:
                    df = pd.DataFrame([data])
        else:
            raise ValueError(f"Unsupported JSON structure: {type(data)}")
        
        return df
    
    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate JSON data.
        
        Args:
            df: DataFrame to validate
        
        Returns:
            Validation result
        """
        issues = []
        warnings = []
        
        if df.empty:
            issues.append("DataFrame is empty")
        
        if len(df.columns) == 0:
            issues.append("No columns found")
        
        # Check for nested structures (columns that are dicts or lists)
        for col in df.columns:
            sample = df[col].dropna().head(1)
            if len(sample) > 0:
                val = sample.iloc[0]
                if isinstance(val, (dict, list)):
                    warnings.append(f"Column '{col}' contains nested structures")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'row_count': len(df),
            'column_count': len(df.columns),
        }

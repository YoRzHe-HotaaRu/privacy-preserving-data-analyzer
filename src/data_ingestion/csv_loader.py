"""Data Ingestion Module - CSV Loader"""

import pandas as pd
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import chardet
except ImportError:
    chardet = None

from .base_loader import DataLoader


class CSVLoader(DataLoader):
    """Load data from CSV files."""
    
    def load(self, source: str, **kwargs) -> pd.DataFrame:
        """
        Load CSV file.
        
        Args:
            source: Path to CSV file
            **kwargs: Additional parameters for pd.read_csv
        
        Returns:
            DataFrame with loaded data
        """
        # Detect encoding if chardet is available
        encoding = kwargs.pop('encoding', None)
        if encoding is None and chardet is not None:
            with open(source, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                encoding = result.get('encoding', 'utf-8')
        elif encoding is None:
            encoding = 'utf-8'
        
        # Default parameters
        default_params = {
            'encoding': encoding,
            'low_memory': False,
            'na_values': ['', 'NA', 'N/A', 'null', 'NULL', 'NaN', 'nan', 'None'],
        }
        
        # Merge with user parameters
        params = {**default_params, **kwargs}
        
        # Load CSV
        df = pd.read_csv(source, **params)
        
        return df
    
    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate CSV data.
        
        Args:
            df: DataFrame to validate
        
        Returns:
            Validation result
        """
        issues = []
        warnings = []
        
        # Check for empty DataFrame
        if df.empty:
            issues.append("DataFrame is empty")
        
        # Check for missing columns
        if len(df.columns) == 0:
            issues.append("No columns found")
        
        # Check for excessive missing values
        if len(df) > 0:
            missing_pct = (df.isnull().sum() / len(df)) * 100
            high_missing = missing_pct[missing_pct > 50]
            if len(high_missing) > 0:
                warnings.append(f"Columns with >50% missing: {high_missing.index.tolist()}")
        
        # Check for duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            warnings.append(f"Found {duplicates} duplicate rows")
        
        # Check for duplicate column names
        if len(df.columns) != len(set(df.columns)):
            issues.append("Duplicate column names found")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'row_count': len(df),
            'column_count': len(df.columns),
        }

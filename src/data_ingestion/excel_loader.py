"""Data Ingestion Module - Excel Loader"""

import pandas as pd
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from .base_loader import DataLoader


class ExcelLoader(DataLoader):
    """Load data from Excel files (.xlsx, .xls)."""
    
    def load(self, source: str, sheet_name: Optional[Union[str, int, List]] = 0, **kwargs) -> pd.DataFrame:
        """
        Load Excel file.
        
        Args:
            source: Path to Excel file
            sheet_name: Sheet name or index (default: 0 for first sheet)
            **kwargs: Additional parameters for pd.read_excel
        
        Returns:
            DataFrame with loaded data
        """
        # Default parameters
        default_params = {
            'sheet_name': sheet_name,
            'na_values': ['', 'NA', 'N/A', 'null', 'NULL', 'NaN', 'nan', 'None'],
        }
        
        # Merge with user parameters
        params = {**default_params, **kwargs}
        
        # Load Excel
        result = pd.read_excel(source, **params)
        
        # If multiple sheets are loaded, concatenate them
        if isinstance(result, dict):
            # Multiple sheets returned as dictionary
            dfs = []
            for sheet, df in result.items():
                df['_sheet_name'] = sheet
                dfs.append(df)
            return pd.concat(dfs, ignore_index=True)
        
        return result
    
    def get_sheet_names(self, source: str) -> List[str]:
        """
        Get list of sheet names in Excel file.
        
        Args:
            source: Path to Excel file
        
        Returns:
            List of sheet names
        """
        excel_file = pd.ExcelFile(source)
        return excel_file.sheet_names
    
    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate Excel data.
        
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
        
        # Check for excessive missing values
        if len(df) > 0:
            missing_pct = (df.isnull().sum() / len(df)) * 100
            high_missing = missing_pct[missing_pct > 50]
            if len(high_missing) > 0:
                warnings.append(f"Columns with >50% missing: {high_missing.index.tolist()}")
        
        # Check for unnamed columns (common in Excel)
        unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
        if unnamed_cols:
            warnings.append(f"Found {len(unnamed_cols)} unnamed columns")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'row_count': len(df),
            'column_count': len(df.columns),
        }

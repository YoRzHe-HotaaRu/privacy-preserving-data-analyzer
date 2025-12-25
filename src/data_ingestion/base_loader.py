"""Data Ingestion Module - Base Loader"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

import pandas as pd


class DataLoader(ABC):
    """Abstract base class for data loaders."""

    @abstractmethod
    def load(self, source: Union[str, Dict], **kwargs) -> pd.DataFrame:
        """
        Load data from source.

        Args:
            source: Data source (file path, URL, database connection)
            **kwargs: Additional parameters

        Returns:
            DataFrame with loaded data
        """
        pass

    @abstractmethod
    def validate(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate loaded data.

        Args:
            df: DataFrame to validate

        Returns:
            Validation result with status and issues
        """
        pass

    def get_schema(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Detect schema of DataFrame.

        Args:
            df: DataFrame to analyze

        Returns:
            Dictionary mapping column names to data types
        """
        schema = {}
        for column in df.columns:
            dtype = df[column].dtype
            if pd.api.types.is_integer_dtype(dtype):
                schema[column] = "integer"
            elif pd.api.types.is_float_dtype(dtype):
                schema[column] = "float"
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                schema[column] = "datetime"
            elif pd.api.types.is_bool_dtype(dtype):
                schema[column] = "boolean"
            else:
                schema[column] = "string"
        return schema

    def get_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get summary statistics of DataFrame.

        Args:
            df: DataFrame to analyze

        Returns:
            Dictionary with summary statistics
        """
        summary = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "missing_counts": df.isnull().sum().to_dict(),
            "missing_percentages": (df.isnull().sum() / len(df) * 100).to_dict() if len(df) > 0 else {},
        }

        # Add numeric summaries
        numeric_cols = df.select_dtypes(include=["number"]).columns
        if len(numeric_cols) > 0:
            summary["numeric_summary"] = df[numeric_cols].describe().to_dict()

        return summary

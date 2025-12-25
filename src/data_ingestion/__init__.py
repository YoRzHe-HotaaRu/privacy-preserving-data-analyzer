"""Data Ingestion Module"""

from .base_loader import DataLoader
from .csv_loader import CSVLoader
from .json_loader import JSONLoader
from .excel_loader import ExcelLoader


def load_file(file_path: str, **kwargs):
    """
    Load a file based on its extension.
    
    Args:
        file_path: Path to the file
        **kwargs: Additional parameters for the loader
    
    Returns:
        DataFrame with loaded data
    """
    file_path_lower = file_path.lower()
    
    if file_path_lower.endswith('.csv'):
        loader = CSVLoader()
    elif file_path_lower.endswith('.json'):
        loader = JSONLoader()
    elif file_path_lower.endswith(('.xlsx', '.xls')):
        loader = ExcelLoader()
    else:
        raise ValueError(f"Unsupported file type: {file_path}")
    
    return loader.load(file_path, **kwargs)


__all__ = [
    'DataLoader',
    'CSVLoader',
    'JSONLoader',
    'ExcelLoader',
    'load_file',
]

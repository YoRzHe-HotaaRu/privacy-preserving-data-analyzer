"""Unit tests for data ingestion module."""

import pytest
import pandas as pd
import tempfile
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_ingestion import CSVLoader, JSONLoader, load_file


class TestCSVLoader:
    """Test CSV loading functionality."""
    
    @pytest.fixture
    def csv_file(self):
        """Create temporary CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("name,email,age\n")
            f.write("John,john@test.com,30\n")
            f.write("Jane,jane@test.com,25\n")
            return f.name
    
    def test_load_csv(self, csv_file):
        """Test CSV loading."""
        loader = CSVLoader()
        df = loader.load(csv_file)
        
        assert len(df) == 2
        assert list(df.columns) == ['name', 'email', 'age']
        assert df['name'].iloc[0] == 'John'
    
    def test_validate_csv(self, csv_file):
        """Test CSV validation."""
        loader = CSVLoader()
        df = loader.load(csv_file)
        result = loader.validate(df)
        
        assert result['valid'] is True
        assert result['row_count'] == 2
        assert result['column_count'] == 3
    
    def test_get_schema(self, csv_file):
        """Test schema detection."""
        loader = CSVLoader()
        df = loader.load(csv_file)
        schema = loader.get_schema(df)
        
        assert 'name' in schema
        assert schema['age'] == 'integer'


class TestJSONLoader:
    """Test JSON loading functionality."""
    
    @pytest.fixture
    def json_file_array(self):
        """Create temporary JSON file with array."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            data = [
                {"name": "John", "age": 30},
                {"name": "Jane", "age": 25}
            ]
            json.dump(data, f)
            return f.name
    
    @pytest.fixture
    def json_file_nested(self):
        """Create temporary JSON file with nested data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            data = {
                "data": [
                    {"name": "John", "age": 30},
                    {"name": "Jane", "age": 25}
                ]
            }
            json.dump(data, f)
            return f.name
    
    def test_load_json_array(self, json_file_array):
        """Test JSON array loading."""
        loader = JSONLoader()
        df = loader.load(json_file_array)
        
        assert len(df) == 2
        assert 'name' in df.columns
    
    def test_load_json_nested(self, json_file_nested):
        """Test nested JSON loading."""
        loader = JSONLoader()
        df = loader.load(json_file_nested)
        
        assert len(df) == 2
        assert df['name'].iloc[0] == 'John'


class TestLoadFile:
    """Test auto file loading."""
    
    def test_load_file_csv(self):
        """Test loading CSV via load_file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("a,b\n1,2\n")
            path = f.name
        
        df = load_file(path)
        assert len(df) == 1
    
    def test_load_file_json(self):
        """Test loading JSON via load_file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([{"a": 1}], f)
            path = f.name
        
        df = load_file(path)
        assert len(df) == 1
    
    def test_load_unsupported_file(self):
        """Test loading unsupported file type."""
        with pytest.raises(ValueError, match="Unsupported file type"):
            load_file("test.xyz")

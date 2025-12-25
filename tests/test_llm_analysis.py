"""Unit tests for LLM analysis module."""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from llm_analysis.llm_client import OpenRouterClient
from llm_analysis.prompt_engine import PrivacyAwarePromptEngine, PRIVACY_SYSTEM_PROMPT
from llm_analysis.insight_generator import InsightGenerator
from llm_analysis.safe_query import (
    SafeQueryValidator,
    ResponseSanitizer,
    preprocess_query,
    FORBIDDEN_KEYWORDS,
    SAFE_KEYWORDS
)


class TestOpenRouterClient:
    """Test OpenRouter LLM client."""
    
    def test_init_without_api_key(self):
        """Test initialization without API key."""
        with patch.dict('os.environ', {}, clear=True):
            client = OpenRouterClient(api_key=None)
            assert not client.is_available()
    
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        with patch('llm_analysis.llm_client.OPENAI_AVAILABLE', True):
            with patch('llm_analysis.llm_client.openai.OpenAI') as mock_openai:
                client = OpenRouterClient(api_key="test-key")
                assert client.api_key == "test-key"
                assert client.model == "bytedance-seed/seed-1.6-flash"
    
    def test_default_model(self):
        """Test default model configuration."""
        client = OpenRouterClient(api_key=None)
        assert client.DEFAULT_MODEL == "bytedance-seed/seed-1.6-flash"
        assert client.BASE_URL == "https://openrouter.ai/api/v1"
    
    def test_is_available_false_when_no_client(self):
        """Test availability check when client not initialized."""
        client = OpenRouterClient(api_key=None)
        assert client.is_available() is False
    
    def test_generate_returns_error_when_unavailable(self):
        """Test generate returns error message when LLM unavailable."""
        client = OpenRouterClient(api_key=None)
        result = client.generate("test prompt")
        assert "[LLM not available" in result
    
    def test_get_stats_initial(self):
        """Test initial statistics."""
        client = OpenRouterClient(api_key=None)
        stats = client.get_stats()
        
        assert stats['request_count'] == 0
        assert stats['total_tokens'] == 0
        assert stats['average_tokens'] == 0
        assert stats['available'] is False
    
    @patch('llm_analysis.llm_client.OPENAI_AVAILABLE', True)
    @patch('llm_analysis.llm_client.openai.OpenAI')
    def test_generate_success(self, mock_openai_class):
        """Test successful generation."""
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage = MagicMock()
        mock_response.usage.total_tokens = 100
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        client = OpenRouterClient(api_key="test-key")
        result = client.generate("test prompt")
        
        assert result == "Test response"
        assert client.request_count == 1
        assert client.token_usage == 100
    
    @patch('llm_analysis.llm_client.OPENAI_AVAILABLE', True)
    @patch('llm_analysis.llm_client.openai.OpenAI')
    def test_generate_with_system_prompt(self, mock_openai_class):
        """Test generation with system prompt."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"
        mock_response.usage = None
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        client = OpenRouterClient(api_key="test-key")
        client.generate("prompt", system_prompt="Be helpful")
        
        # Verify system prompt was included
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs['messages']
        assert len(messages) == 2
        assert messages[0]['role'] == 'system'


class TestPrivacyAwarePromptEngine:
    """Test privacy-aware prompt engine."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up prompt engine for each test."""
        self.engine = PrivacyAwarePromptEngine()
    
    def test_get_system_prompt(self):
        """Test getting system prompt."""
        prompt = self.engine.get_system_prompt()
        assert "privacy" in prompt.lower()
        assert "PII" in prompt
        assert "NEVER" in prompt
    
    def test_system_prompt_contains_privacy_principles(self):
        """Test system prompt contains core privacy principles."""
        prompt = self.engine.get_system_prompt()
        assert "CORE PRIVACY PRINCIPLES" in prompt
        assert "re-identify" in prompt.lower()
        assert "anonymized" in prompt.lower()
    
    def test_create_analysis_prompt(self):
        """Test creating analysis prompt."""
        data_summary = "Dataset: 100 rows × 5 columns"
        prompt = self.engine.create_analysis_prompt(data_summary, 'general')
        
        assert data_summary in prompt
        assert "patterns" in prompt.lower()
        assert "privacy" in prompt.lower()
        assert "anonymized" in prompt.lower()
    
    def test_create_qa_prompt(self):
        """Test creating Q&A prompt."""
        question = "What is the average salary?"
        context = "Dataset summary..."
        
        prompt = self.engine.create_qa_prompt(question, context)
        
        assert question in prompt
        assert context in prompt
        assert "PRIVACY CONSTRAINTS" in prompt
    
    def test_create_summary_prompt(self):
        """Test creating summary prompt."""
        df_summary = {
            'row_count': 100,
            'column_count': 5,
            'columns': ['a', 'b', 'c'],
            'dtypes': {'a': 'int64', 'b': 'float64'},
            'missing_percentages': {'a': 0.0, 'b': 5.0}
        }
        
        prompt = self.engine.create_summary_prompt(df_summary)
        
        assert "100" in prompt
        assert "5" in prompt
        assert "aggregate" in prompt.lower()
    
    def test_format_dataframe_for_llm(self, sample_dataframe):
        """Test DataFrame formatting for LLM."""
        formatted = self.engine.format_dataframe_for_llm(sample_dataframe)
        
        assert "rows" in formatted.lower() or "3" in formatted
        assert "columns" in formatted.lower()
        assert "Data Types" in formatted
    
    def test_format_dataframe_includes_numeric_stats(self, sample_dataframe):
        """Test DataFrame formatting includes numeric statistics."""
        formatted = self.engine.format_dataframe_for_llm(sample_dataframe)
        
        assert "Numeric Column Statistics" in formatted
    
    def test_format_dataframe_includes_categorical(self, sample_dataframe):
        """Test DataFrame formatting includes categorical summaries."""
        formatted = self.engine.format_dataframe_for_llm(sample_dataframe)
        
        assert "Categorical Column Value Counts" in formatted


class TestSafeQueryValidator:
    """Test safe query validation."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up validator for each test."""
        self.validator = SafeQueryValidator()
    
    def test_safe_aggregate_query(self):
        """Test validation of safe aggregate query."""
        query = "What is the average salary by department?"
        is_safe, issues = self.validator.validate(query)
        
        assert is_safe is True
        assert len(issues) == 0
    
    def test_unsafe_individual_query(self):
        """Test validation of unsafe individual-level query."""
        query = "Who is the person with the highest salary?"
        is_safe, issues = self.validator.validate(query)
        
        assert is_safe is False
        assert len(issues) > 0
    
    @pytest.mark.parametrize("unsafe_keyword", [
        "specific person",
        "individual record",
        "whose email",
        "find the person",
        "identify",
        "ssn"
    ])
    def test_forbidden_keywords_detected(self, unsafe_keyword):
        """Test forbidden keywords are detected."""
        query = f"Query about {unsafe_keyword}"
        is_safe, issues = self.validator.validate(query)
        
        assert is_safe is False
    
    def test_has_safe_keywords_true(self):
        """Test safe keyword detection - positive."""
        query = "What is the average and total count?"
        assert self.validator.has_safe_keywords(query) is True
    
    def test_has_safe_keywords_false(self):
        """Test safe keyword detection - negative."""
        query = "Show me individual records"
        assert self.validator.has_safe_keywords(query) is False
    
    @pytest.mark.parametrize("safe_keyword", SAFE_KEYWORDS)
    def test_all_safe_keywords_recognized(self, safe_keyword):
        """Test all safe keywords are recognized."""
        query = f"Calculate the {safe_keyword} value"
        assert self.validator.has_safe_keywords(query) is True


class TestResponseSanitizer:
    """Test response sanitization."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up sanitizer for each test."""
        self.sanitizer = ResponseSanitizer()
    
    def test_sanitize_email(self):
        """Test email sanitization."""
        response = "Contact john@example.com for more info"
        sanitized, counts = self.sanitizer.sanitize(response)
        
        assert "john@example.com" not in sanitized
        assert "[REDACTED]" in sanitized
        assert counts.get('email', 0) >= 1
    
    def test_sanitize_phone(self):
        """Test phone number sanitization."""
        response = "Call 555-123-4567 for support"
        sanitized, counts = self.sanitizer.sanitize(response)
        
        assert "555-123-4567" not in sanitized
        assert "[REDACTED]" in sanitized
        assert counts.get('phone', 0) >= 1
    
    def test_sanitize_ssn(self):
        """Test SSN sanitization."""
        response = "SSN: 123-45-6789"
        sanitized, counts = self.sanitizer.sanitize(response)
        
        assert "123-45-6789" not in sanitized
        assert "[REDACTED]" in sanitized
    
    def test_sanitize_credit_card(self):
        """Test credit card sanitization."""
        response = "Card: 1234-5678-9012-3456"
        sanitized, counts = self.sanitizer.sanitize(response)
        
        assert "1234-5678-9012-3456" not in sanitized
        assert "[REDACTED]" in sanitized
    
    def test_sanitize_clean_text(self):
        """Test sanitization of text without PII."""
        response = "The average salary is $75,000"
        sanitized, counts = self.sanitizer.sanitize(response)
        
        assert sanitized == response
        assert len(counts) == 0
    
    def test_contains_pii_true(self):
        """Test PII detection - positive."""
        assert self.sanitizer.contains_pii("Email: test@example.com") is True
    
    def test_contains_pii_false(self):
        """Test PII detection - negative."""
        assert self.sanitizer.contains_pii("No PII here") is False
    
    def test_sanitize_multiple_pii(self):
        """Test sanitization of multiple PII types."""
        response = "Contact john@test.com or call 555-123-4567"
        sanitized, counts = self.sanitizer.sanitize(response)
        
        assert "john@test.com" not in sanitized
        assert "555-123-4567" not in sanitized
        assert sanitized.count("[REDACTED]") >= 2


class TestPreprocessQuery:
    """Test query preprocessing."""
    
    def test_adds_privacy_reminder(self):
        """Test that privacy reminder is added."""
        query = "What is the average?"
        processed = preprocess_query(query)
        
        assert query in processed
        assert "PRIVACY REMINDER" in processed
        assert "aggregate statistics" in processed.lower()


class TestInsightGenerator:
    """Test insight generator."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up generator for each test."""
        self.generator = InsightGenerator(api_key=None)
    
    def test_is_available_without_api_key(self):
        """Test availability without API key."""
        assert self.generator.is_available() is False
    
    def test_generate_insights_structure(self, sample_dataframe):
        """Test insight generation returns proper structure."""
        result = self.generator.generate_insights(sample_dataframe)
        
        assert 'analysis_type' in result
        assert 'insights' in result
        assert 'data_summary' in result
        assert 'llm_stats' in result
    
    def test_generate_insights_unavailable_llm(self, sample_dataframe):
        """Test insight generation when LLM unavailable."""
        result = self.generator.generate_insights(sample_dataframe)
        
        assert "[LLM not available" in result['insights']
    
    def test_answer_question_structure(self, sample_dataframe):
        """Test Q&A returns proper structure."""
        result = self.generator.answer_question(sample_dataframe, "What is the average age?")
        
        assert 'question' in result
        assert 'answer' in result
        assert 'llm_stats' in result
        assert result['question'] == "What is the average age?"
    
    def test_generate_summary_structure(self, sample_dataframe):
        """Test summary generation returns proper structure."""
        result = self.generator.generate_summary(sample_dataframe)
        
        assert 'summary' in result
        assert 'data_info' in result
        assert 'llm_stats' in result
        assert result['data_info']['row_count'] == len(sample_dataframe)
    
    @patch('llm_analysis.insight_generator.OpenRouterClient')
    def test_generate_insights_with_mock_client(self, mock_client_class, sample_dataframe):
        """Test insight generation with mocked client."""
        mock_instance = MagicMock()
        mock_instance.is_available.return_value = True
        mock_instance.generate.return_value = "Test insights"
        mock_instance.get_stats.return_value = {'request_count': 1}
        mock_client_class.return_value = mock_instance
        
        generator = InsightGenerator(api_key="test-key")
        result = generator.generate_insights(sample_dataframe)
        
        assert result['insights'] == "Test insights"

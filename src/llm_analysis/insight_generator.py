"""LLM Analysis Module - Insight Generator"""

from typing import Dict, Any, List, Optional
import pandas as pd

from .llm_client import OpenRouterClient
from .prompt_engine import PrivacyAwarePromptEngine


class InsightGenerator:
    """Generate insights from anonymized data using LLM."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize insight generator.
        
        Args:
            api_key: OpenRouter API key
        """
        self.client = OpenRouterClient(api_key)
        self.prompt_engine = PrivacyAwarePromptEngine()
    
    def generate_insights(self, df: pd.DataFrame, 
                         analysis_type: str = 'general') -> Dict[str, Any]:
        """
        Generate insights from a DataFrame.
        
        Args:
            df: Anonymized DataFrame
            analysis_type: Type of analysis
        
        Returns:
            Dictionary with insights
        """
        # Format data for LLM
        data_summary = self.prompt_engine.format_dataframe_for_llm(df)
        
        # Create prompt
        prompt = self.prompt_engine.create_analysis_prompt(data_summary, analysis_type)
        
        # Generate insights
        system_prompt = self.prompt_engine.get_system_prompt()
        response = self.client.generate(prompt, system_prompt=system_prompt)
        
        return {
            'analysis_type': analysis_type,
            'insights': response,
            'data_summary': {
                'rows': len(df),
                'columns': len(df.columns)
            },
            'llm_stats': self.client.get_stats()
        }
    
    def answer_question(self, df: pd.DataFrame, question: str) -> Dict[str, Any]:
        """
        Answer a question about the data.
        
        Args:
            df: Anonymized DataFrame
            question: User question
        
        Returns:
            Dictionary with answer
        """
        # Format data context
        data_context = self.prompt_engine.format_dataframe_for_llm(df)
        
        # Create prompt
        prompt = self.prompt_engine.create_qa_prompt(question, data_context)
        
        # Generate answer
        system_prompt = self.prompt_engine.get_system_prompt()
        response = self.client.generate(prompt, system_prompt=system_prompt)
        
        return {
            'question': question,
            'answer': response,
            'llm_stats': self.client.get_stats()
        }
    
    def generate_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate a summary of the dataset.
        
        Args:
            df: Anonymized DataFrame
        
        Returns:
            Dictionary with summary
        """
        # Get DataFrame summary
        df_summary = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'missing_percentages': (df.isnull().sum() / len(df) * 100).to_dict() if len(df) > 0 else {}
        }
        
        # Create prompt
        prompt = self.prompt_engine.create_summary_prompt(df_summary)
        
        # Generate summary
        system_prompt = self.prompt_engine.get_system_prompt()
        response = self.client.generate(prompt, system_prompt=system_prompt)
        
        return {
            'summary': response,
            'data_info': df_summary,
            'llm_stats': self.client.get_stats()
        }
    
    def is_available(self) -> bool:
        """Check if LLM is available."""
        return self.client.is_available()

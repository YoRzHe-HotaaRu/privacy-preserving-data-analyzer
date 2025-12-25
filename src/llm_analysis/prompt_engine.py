"""LLM Analysis Module - Privacy-Aware Prompt Engine"""

from typing import Dict, Any
import pandas as pd


PRIVACY_SYSTEM_PROMPT = """You are a specialized data analysis assistant with strict privacy constraints.

CORE PRIVACY PRINCIPLES:
1. NEVER include, reference, or attempt to reconstruct PII
2. Work ONLY with anonymized or aggregated data
3. Do NOT attempt to re-identify individuals
4. Focus on patterns, trends, correlations, and statistical insights
5. If asked about individual records, REFUSE and explain privacy constraints

PROTECTED INFORMATION:
- Names, emails, phone numbers, SSNs, addresses, dates of birth
- Medical record numbers, credit card numbers, bank account numbers
- Any other unique identifiers

ANALYSIS GUIDELINES:
1. Identify statistically significant patterns
2. Highlight correlations between variables
3. Detect anomalies or outliers
4. Provide actionable recommendations
5. Quantify uncertainty in your analysis
6. Clearly state assumptions and limitations

RESPONSE FORMAT:
- Clear, structured insights
- Statistical significance indicators
- Confidence levels for claims
- Limitations and assumptions
- Recommendations for further analysis"""


class PrivacyAwarePromptEngine:
    """Generate privacy-preserving prompts for LLM analysis."""
    
    def __init__(self):
        self.system_prompt = PRIVACY_SYSTEM_PROMPT
    
    def get_system_prompt(self) -> str:
        """Get the privacy system prompt."""
        return self.system_prompt
    
    def create_analysis_prompt(self, data_summary: str, 
                               analysis_type: str = 'general') -> str:
        """
        Create a prompt for data analysis.
        
        Args:
            data_summary: Summary statistics of the data
            analysis_type: Type of analysis (general, trends, correlations)
        
        Returns:
            Formatted prompt
        """
        prompt = f"""Analyze the following anonymized data summary:

{data_summary}

Please provide insights on {analysis_type}.

Your analysis should include:
1. Key patterns and trends observed
2. Notable correlations between variables
3. Significant anomalies or outliers
4. Statistical significance of findings
5. Potential causes or explanations
6. Recommendations for further investigation

IMPORTANT:
- Work ONLY with the aggregated/anonymized data provided
- Do NOT attempt to identify individuals or specific records
- Focus on population-level insights
- Clearly state any assumptions or limitations
- Provide confidence levels for your claims

Format your response with clear headings and bullet points."""
        return prompt
    
    def create_qa_prompt(self, question: str, data_context: str) -> str:
        """
        Create a prompt for question answering.
        
        Args:
            question: User's question
            data_context: Context about the data
        
        Returns:
            Formatted prompt
        """
        prompt = f"""Context: {data_context}

Question: {question}

Please answer this question based on the anonymized data provided.

PRIVACY CONSTRAINTS:
- You may ONLY use the aggregated/anonymized data provided
- If the question requires individual-level information that could compromise privacy, REFUSE
- Explain WHY you cannot answer if it violates privacy constraints
- Suggest an alternative approach using aggregated data if possible

Your response should:
1. Directly answer the question if possible with provided data
2. Explain privacy constraints if the question cannot be answered
3. Suggest alternative analyses that could address the underlying need
4. Provide confidence in your answer
5. Note any assumptions or limitations"""
        return prompt
    
    def create_summary_prompt(self, df_summary: Dict[str, Any]) -> str:
        """
        Create a prompt for data summarization.
        
        Args:
            df_summary: DataFrame summary statistics
        
        Returns:
            Formatted prompt
        """
        prompt = f"""Provide a comprehensive summary of the following dataset:

Dataset Overview:
- Rows: {df_summary.get('row_count', 'N/A')}
- Columns: {df_summary.get('column_count', 'N/A')}
- Column Names: {df_summary.get('columns', [])}

Data Types:
{df_summary.get('dtypes', {})}

Missing Values:
{df_summary.get('missing_percentages', {})}

Please provide:
1. A brief overview of the dataset structure
2. Data quality assessment
3. Key observations about the data distribution
4. Recommendations for data cleaning (if needed)
5. Potential analysis directions

Remember: Focus ONLY on aggregate statistics. Do NOT reference individual records."""
        return prompt
    
    def format_dataframe_for_llm(self, df: pd.DataFrame, max_rows: int = 10) -> str:
        """
        Format DataFrame summary for LLM consumption.
        
        Args:
            df: DataFrame to summarize
            max_rows: Maximum sample rows to include
        
        Returns:
            Formatted string summary
        """
        summary = []
        
        # Basic info
        summary.append(f"Dataset: {len(df)} rows × {len(df.columns)} columns")
        summary.append(f"\nColumns: {', '.join(df.columns.tolist())}")
        
        # Data types
        summary.append("\nData Types:")
        for col, dtype in df.dtypes.items():
            summary.append(f"  - {col}: {dtype}")
        
        # Numeric summary
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary.append("\nNumeric Column Statistics:")
            desc = df[numeric_cols].describe()
            summary.append(desc.to_string())
        
        # Categorical summary
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(cat_cols) > 0:
            summary.append("\nCategorical Column Value Counts (top 5):")
            for col in cat_cols[:5]:  # Limit to first 5 categorical columns
                counts = df[col].value_counts().head(5)
                summary.append(f"\n  {col}:")
                for val, count in counts.items():
                    summary.append(f"    - {val}: {count}")
        
        # Missing values
        missing = df.isnull().sum()
        if missing.any():
            summary.append("\nMissing Values:")
            for col, count in missing[missing > 0].items():
                pct = count / len(df) * 100
                summary.append(f"  - {col}: {count} ({pct:.1f}%)")
        
        return "\n".join(summary)

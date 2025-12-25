"""LLM Analysis Module - Safe Query System"""

import re
from typing import Dict, Any, List, Tuple


# Forbidden keywords that might lead to PII extraction
FORBIDDEN_KEYWORDS = [
    'specific person', 'individual record', 'who is', 'whose',
    'find the person', 'identify', 'name of', 'contact of',
    'address of', 'email of', 'phone of', 'ssn', 'social security',
    'credit card', 'bank account', 'password', 'secret'
]

# Keywords that indicate safe aggregate queries
SAFE_KEYWORDS = [
    'average', 'mean', 'median', 'total', 'count', 'sum',
    'distribution', 'percentage', 'trend', 'correlation',
    'pattern', 'aggregate', 'overall', 'general', 'summary'
]


class SafeQueryValidator:
    """Validate queries for privacy safety."""
    
    def __init__(self):
        self.forbidden_patterns = [
            re.compile(keyword, re.IGNORECASE) 
            for keyword in FORBIDDEN_KEYWORDS
        ]
    
    def validate(self, query: str) -> Tuple[bool, List[str]]:
        """
        Validate if a query is safe from a privacy perspective.
        
        Args:
            query: User query
        
        Returns:
            Tuple of (is_safe, list of issues)
        """
        issues = []
        
        # Check for forbidden keywords
        for pattern in self.forbidden_patterns:
            if pattern.search(query):
                issues.append(f"Query contains potentially risky phrase: '{pattern.pattern}'")
        
        # Check if query seems to request individual data
        individual_patterns = [
            r'\b(one|single|specific|particular)\s+(person|individual|record|row)\b',
            r'\bwho\s+(is|has|was)\b',
            r'\bwhose\b',
            r'\bfind\s+the\b',
        ]
        
        for pattern in individual_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                issues.append(f"Query appears to request individual-level data")
                break
        
        return len(issues) == 0, issues
    
    def has_safe_keywords(self, query: str) -> bool:
        """Check if query contains safe aggregate keywords."""
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in SAFE_KEYWORDS)


class ResponseSanitizer:
    """Sanitize LLM responses to prevent accidental PII leakage."""
    
    def __init__(self):
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
            'ssn': r'\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b',
            'credit_card': r'\b(?:\d{4}[-.\s]?){3}\d{4}\b',
            'ip': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        }
    
    def sanitize(self, response: str) -> Tuple[str, Dict[str, int]]:
        """
        Sanitize a response by removing potential PII.
        
        Args:
            response: LLM response text
        
        Returns:
            Tuple of (sanitized_response, count of redactions by type)
        """
        sanitized = response
        redaction_counts = {}
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, sanitized)
            if matches:
                redaction_counts[pii_type] = len(matches)
                sanitized = re.sub(pattern, '[REDACTED]', sanitized)
        
        return sanitized, redaction_counts
    
    def contains_pii(self, response: str) -> bool:
        """Check if response contains potential PII."""
        for pattern in self.pii_patterns.values():
            if re.search(pattern, response):
                return True
        return False


def preprocess_query(query: str) -> str:
    """
    Preprocess a query to add privacy context.
    
    Args:
        query: Original query
    
    Returns:
        Query with privacy reminders
    """
    privacy_reminder = (
        "\n\n[PRIVACY REMINDER: Respond using only aggregate statistics. "
        "Do not include any individual-level data or PII in your response.]"
    )
    return query + privacy_reminder

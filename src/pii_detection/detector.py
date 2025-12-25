"""PII Detection Module - Main Detector"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import yaml

try:
    from presidio_analyzer import AnalyzerEngine, RecognizerResult
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False
    RecognizerResult = None


class PIIDetector:
    """Main PII detection engine using Presidio."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize PII detector.
        
        Args:
            config_path: Path to PII configuration file
        """
        self.config = self._load_config(config_path)
        self.analyzer = None
        
        if PRESIDIO_AVAILABLE:
            self._setup_analyzer()
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load PII configuration."""
        if config_path is None:
            # Try default paths
            possible_paths = [
                Path(__file__).parent.parent / 'config' / 'pii_entities.yaml',
                Path('src/config/pii_entities.yaml'),
            ]
            for path in possible_paths:
                if path.exists():
                    config_path = str(path)
                    break
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        
        # Default config
        return {
            'entities': {
                'PERSON': {'enabled': True, 'confidence_threshold': 0.85, 'anonymization': 'mask'},
                'EMAIL_ADDRESS': {'enabled': True, 'confidence_threshold': 0.90, 'anonymization': 'mask'},
                'PHONE_NUMBER': {'enabled': True, 'confidence_threshold': 0.85, 'anonymization': 'mask'},
                'US_SSN': {'enabled': True, 'confidence_threshold': 0.95, 'anonymization': 'suppression'},
                'CREDIT_CARD': {'enabled': True, 'confidence_threshold': 0.95, 'anonymization': 'suppression'},
                'IP_ADDRESS': {'enabled': True, 'confidence_threshold': 0.90, 'anonymization': 'generalize'},
                'DATE_TIME': {'enabled': True, 'confidence_threshold': 0.85, 'anonymization': 'generalize'},
                'LOCATION': {'enabled': True, 'confidence_threshold': 0.80, 'anonymization': 'generalize'},
            }
        }
    
    def _setup_analyzer(self):
        """Setup Presidio analyzer."""
        try:
            self.analyzer = AnalyzerEngine()
            # Register custom recognizers
            from .custom_entities import register_custom_recognizers
            register_custom_recognizers(self.analyzer)
        except Exception as e:
            print(f"Warning: Could not initialize Presidio analyzer: {e}")
            self.analyzer = None
    
    def detect(self, text: str, language: str = 'en') -> List[Dict[str, Any]]:
        """
        Detect PII in text.
        
        Args:
            text: Input text to analyze
            language: Language code (default: 'en')
        
        Returns:
            List of PII detection results
        """
        if not text or not isinstance(text, str):
            return []
        
        if self.analyzer is None:
            # Fallback to simple regex-based detection
            return self._detect_fallback(text)
        
        try:
            # Get enabled entities
            entities = self._get_enabled_entities()
            
            # Analyze text
            results = self.analyzer.analyze(
                text=text,
                language=language,
                entities=entities
            )
            
            # Filter by confidence threshold and convert to dict
            filtered_results = []
            for result in results:
                entity_config = self.config.get('entities', {}).get(result.entity_type, {})
                threshold = entity_config.get('confidence_threshold', 0.8)
                
                if result.score >= threshold:
                    filtered_results.append({
                        'entity_type': result.entity_type,
                        'start': result.start,
                        'end': result.end,
                        'score': result.score,
                        'text': text[result.start:result.end],
                    })
            
            return filtered_results
        except Exception as e:
            print(f"Error during PII detection: {e}")
            return self._detect_fallback(text)
    
    def _get_enabled_entities(self) -> List[str]:
        """Get list of enabled PII entity types."""
        return [
            entity for entity, config in self.config.get('entities', {}).items()
            if config.get('enabled', True)
        ]
    
    def _detect_fallback(self, text: str) -> List[Dict[str, Any]]:
        """Fallback regex-based PII detection."""
        import re
        
        results = []
        patterns = {
            'EMAIL_ADDRESS': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'PHONE_NUMBER': r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
            'US_SSN': r'\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b',
            'CREDIT_CARD': r'\b(?:\d{4}[-.\s]?){3}\d{4}\b',
            'IP_ADDRESS': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        }
        
        for entity_type, pattern in patterns.items():
            entity_config = self.config.get('entities', {}).get(entity_type, {})
            if not entity_config.get('enabled', True):
                continue
            
            for match in re.finditer(pattern, text, re.IGNORECASE):
                results.append({
                    'entity_type': entity_type,
                    'start': match.start(),
                    'end': match.end(),
                    'score': 0.85,  # Default confidence for regex matches
                    'text': match.group(),
                })
        
        return results
    
    def detect_batch(self, texts: List[str], language: str = 'en') -> List[List[Dict[str, Any]]]:
        """
        Detect PII in multiple texts.
        
        Args:
            texts: List of texts to analyze
            language: Language code
        
        Returns:
            List of lists of PII detection results
        """
        return [self.detect(text, language) for text in texts]
    
    def get_pii_summary(self, text: str) -> Dict[str, Any]:
        """
        Get a summary of PII found in text.
        
        Args:
            text: Input text to analyze
        
        Returns:
            Dictionary with PII counts and types
        """
        results = self.detect(text)
        
        summary = {
            'total_pii': len(results),
            'by_type': {}
        }
        
        for result in results:
            entity_type = result['entity_type']
            if entity_type not in summary['by_type']:
                summary['by_type'][entity_type] = {
                    'count': 0,
                    'instances': []
                }
            summary['by_type'][entity_type]['count'] += 1
            summary['by_type'][entity_type]['instances'].append({
                'text': result['text'],
                'score': result['score'],
            })
        
        return summary
    
    def get_entity_config(self, entity_type: str) -> Dict[str, Any]:
        """Get configuration for an entity type."""
        return self.config.get('entities', {}).get(entity_type, {})

"""Anonymization Module - Main Anonymizer"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import yaml

from .strategies import Tokenizer, generalize, hash_value, mask, perturb, suppress


class DataAnonymizer:
    """Main anonymization module with multiple strategies."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize anonymizer.

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.tokenizer = Tokenizer()
        self.hash_salt = os.urandom(16).hex()

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load anonymization configuration."""
        if config_path is None:
            possible_paths = [
                Path(__file__).parent.parent / "config" / "default_config.yaml",
                Path("src/config/default_config.yaml"),
            ]
            for path in possible_paths:
                if path.exists():
                    config_path = str(path)
                    break

        if config_path and Path(config_path).exists():
            with open(config_path, "r") as f:
                return yaml.safe_load(f)

        # Default config
        return {
            "anonymization": {
                "PERSON": "mask",
                "EMAIL_ADDRESS": "mask",
                "PHONE_NUMBER": "mask",
                "US_SSN": "suppression",
                "CREDIT_CARD": "suppression",
                "IP_ADDRESS": "generalize",
                "DATE_TIME": "generalize",
                "LOCATION": "generalize",
            }
        }

    def get_strategy(self, entity_type: str) -> str:
        """Get anonymization strategy for entity type."""
        return self.config.get("anonymization", {}).get(entity_type, "mask")

    def apply_strategy(self, value: str, entity_type: str, strategy: str = None) -> str:
        """
        Apply anonymization strategy to value.

        Args:
            value: Original value
            entity_type: Type of PII entity
            strategy: Strategy to use (defaults to config)

        Returns:
            Anonymized value
        """
        if strategy is None:
            strategy = self.get_strategy(entity_type)

        # Normalize strategy names
        strategy = strategy.lower().strip()
        
        if strategy in ("suppression", "suppress"):
            return suppress(value, entity_type)
        elif strategy == "mask":
            return mask(value, entity_type)
        elif strategy in ("generalize", "generalization"):
            return generalize(value, entity_type)
        elif strategy == "perturb":
            return perturb(value)
        elif strategy == "tokenize":
            return self.tokenizer.tokenize(value)
        elif strategy == "hash":
            return hash_value(value, self.hash_salt)
        else:
            return mask(value, entity_type)  # Default

    def anonymize_text(self, text: str, pii_results: List[Dict[str, Any]]) -> str:
        """
        Anonymize text based on detected PII.

        Args:
            text: Input text
            pii_results: List of PII detection results

        Returns:
            Anonymized text
        """
        if not pii_results:
            return text

        # Sort results by start position (reverse order for replacement)
        sorted_results = sorted(pii_results, key=lambda x: x["start"], reverse=True)

        anonymized_text = text
        for result in sorted_results:
            entity_type = result["entity_type"]
            original_value = text[result["start"] : result["end"]]

            # Apply anonymization
            anonymized_value = self.apply_strategy(original_value, entity_type)

            # Replace in text
            anonymized_text = anonymized_text[: result["start"]] + anonymized_value + anonymized_text[result["end"] :]

        return anonymized_text

    def anonymize_dataframe(self, df: pd.DataFrame, pii_columns: Dict[str, str]) -> pd.DataFrame:
        """
        Anonymize specified columns in a DataFrame.

        Args:
            df: Input DataFrame
            pii_columns: Dict mapping column names to entity types

        Returns:
            Anonymized DataFrame
        """
        anonymized_df = df.copy()

        for column, entity_type in pii_columns.items():
            if column in anonymized_df.columns:
                strategy = self.get_strategy(entity_type)
                anonymized_df[column] = anonymized_df[column].apply(
                    lambda x: self.apply_strategy(str(x), entity_type, strategy) if pd.notna(x) else x
                )

        return anonymized_df

    def anonymize_dataframe_auto(self, df: pd.DataFrame, pii_detector=None) -> tuple:
        """
        Automatically detect and anonymize PII in DataFrame.

        Args:
            df: Input DataFrame
            pii_detector: Optional PIIDetector instance

        Returns:
            Tuple of (anonymized_df, detection_report)
        """
        from ..pii_detection import PIIDetector

        if pii_detector is None:
            pii_detector = PIIDetector()

        anonymized_df = df.copy()
        detection_report = {}

        for column in df.columns:
            # Sample values to detect PII
            sample_values = df[column].dropna().head(10).astype(str).tolist()

            # Check for PII in samples
            all_pii = []
            for value in sample_values:
                pii = pii_detector.detect(value)
                if pii:
                    all_pii.extend(pii)

            if all_pii:
                # Determine most common entity type
                entity_counts = {}
                for pii_item in all_pii:
                    entity_type = pii_item["entity_type"]
                    entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1

                most_common_entity = max(entity_counts, key=entity_counts.get)

                # Anonymize column
                strategy = self.get_strategy(most_common_entity)
                anonymized_df[column] = anonymized_df[column].apply(
                    lambda x: self.apply_strategy(str(x), most_common_entity, strategy) if pd.notna(x) else x
                )

                detection_report[column] = {
                    "entity_type": most_common_entity,
                    "count": entity_counts[most_common_entity],
                    "strategy": strategy,
                }

        return anonymized_df, detection_report

    def get_token_mapping(self) -> dict:
        """Get the tokenization mapping (for authorized reversals)."""
        return self.tokenizer.get_mapping()

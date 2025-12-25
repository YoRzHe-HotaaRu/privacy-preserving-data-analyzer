"""PII Detection Module"""

from .custom_entities import register_custom_recognizers
from .detector import PIIDetector

__all__ = [
    "PIIDetector",
    "register_custom_recognizers",
]

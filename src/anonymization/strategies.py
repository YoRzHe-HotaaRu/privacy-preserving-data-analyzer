"""Anonymization Module - Strategies"""

import hashlib
import secrets
from datetime import datetime
from typing import Optional

import numpy as np


def suppress(value: str, entity_type: str = None) -> str:
    """
    Completely remove the value.

    Args:
        value: Original value
        entity_type: Type of entity

    Returns:
        Redacted placeholder
    """
    return "[REDACTED]"


def mask_email(email: str) -> str:
    """
    Mask email: j***@email.com

    Args:
        email: Email address

    Returns:
        Masked email
    """
    try:
        username, domain = email.split("@")
        if len(username) <= 2:
            masked_username = "*" * len(username)
        else:
            masked_username = username[0] + "*" * (len(username) - 1)
        return f"{masked_username}@{domain}"
    except ValueError:
        return "***@***.***"


def mask_phone(phone: str) -> str:
    """
    Mask phone: +1 (***) ***-1234

    Args:
        phone: Phone number

    Returns:
        Masked phone number
    """
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) >= 10:
        return f"+1 (***) ***-{digits[-4:]}"
    elif len(digits) >= 7:
        return f"(***) ***-{digits[-4:]}"
    elif len(digits) >= 4:
        return f"***-{digits[-4:]}"
    else:
        return "***"


def mask_name(name: str) -> str:
    """
    Mask name: J*** D***

    Args:
        name: Full name

    Returns:
        Masked name
    """
    parts = name.split()
    masked_parts = []
    for part in parts:
        if len(part) <= 1:
            masked_parts.append(part)
        else:
            masked_parts.append(part[0] + "*" * (len(part) - 1))
    return " ".join(masked_parts)


def mask(value: str, entity_type: str) -> str:
    """
    Mask a value based on entity type.

    Args:
        value: Original value
        entity_type: Type of entity

    Returns:
        Masked value
    """
    if entity_type == "EMAIL_ADDRESS":
        return mask_email(value)
    elif entity_type == "PHONE_NUMBER":
        return mask_phone(value)
    elif entity_type == "PERSON":
        return mask_name(value)
    elif entity_type in ["US_SSN"]:
        digits = "".join(c for c in value if c.isdigit())
        if len(digits) >= 4:
            return f"***-**-{digits[-4:]}"
        return "***-**-****"
    elif entity_type == "CREDIT_CARD":
        digits = "".join(c for c in value if c.isdigit())
        if len(digits) >= 4:
            return f"****-****-****-{digits[-4:]}"
        return "****-****-****-****"
    else:
        if len(value) <= 2:
            return "***"
        return value[0] + "***" + value[-1]


def generalize_age(age_str: str) -> str:
    """
    Generalize age to ranges.

    Args:
        age_str: Age as string

    Returns:
        Age range
    """
    try:
        age = int(age_str)
        if age < 18:
            return "<18"
        elif age < 25:
            return "18-24"
        elif age < 35:
            return "25-34"
        elif age < 45:
            return "35-44"
        elif age < 55:
            return "45-54"
        elif age < 65:
            return "55-64"
        else:
            return "65+"
    except (ValueError, TypeError):
        return age_str


def generalize_date(date_str: str, level: str = "month") -> str:
    """
    Generalize date to different levels.

    Args:
        date_str: Date string
        level: Generalization level (year, month, quarter)

    Returns:
        Generalized date
    """
    date_formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]

    dt = None
    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            break
        except ValueError:
            continue

    if dt is None:
        return date_str

    if level == "year":
        return str(dt.year)
    elif level == "month":
        return dt.strftime("%Y-%m")
    elif level == "quarter":
        quarter = (dt.month - 1) // 3 + 1
        return f"{dt.year}-Q{quarter}"
    else:
        return date_str


def generalize(value: str, entity_type: str) -> str:
    """
    Generalize a value based on entity type.

    Args:
        value: Original value
        entity_type: Type of entity

    Returns:
        Generalized value
    """
    if entity_type == "DATE_TIME" or entity_type == "DATE_OF_BIRTH":
        return generalize_date(value)
    elif entity_type == "AGE":
        return generalize_age(value)
    elif entity_type == "LOCATION":
        return "[LOCATION]"
    elif entity_type == "IP_ADDRESS":
        parts = value.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.*.*"
        return "[IP_ADDRESS]"
    else:
        return f"[{entity_type}]"


def perturb(value: str, noise_level: float = 0.05, bounds: tuple = None) -> str:
    """
    Add controlled noise to numerical values.

    Args:
        value: Original value
        noise_level: Standard deviation as percentage of value
        bounds: Optional (min, max) tuple

    Returns:
        Perturbed value
    """
    try:
        num = float(value)
    except (ValueError, TypeError):
        return value

    # Calculate noise
    std_dev = abs(num) * noise_level if num != 0 else noise_level
    noise = np.random.normal(0, std_dev)
    perturbed = num + noise

    # Clamp to bounds if provided
    if bounds:
        perturbed = max(bounds[0], min(bounds[1], perturbed))

    # Round to reasonable precision
    if abs(perturbed) < 1:
        return str(round(perturbed, 3))
    elif abs(perturbed) < 100:
        return str(round(perturbed, 2))
    else:
        return str(round(perturbed, 1))


class Tokenizer:
    """Reversible tokenization for PII."""

    def __init__(self):
        self.token_map = {}  # token -> original_value
        self.reverse_map = {}  # original_value -> token
        self.counter = 0

    def tokenize(self, value: str) -> str:
        """
        Replace value with token.

        Args:
            value: Original value

        Returns:
            Token string
        """
        if value in self.reverse_map:
            return self.reverse_map[value]

        token = f"[TOKEN_{self.counter}]"
        self.counter += 1

        self.token_map[token] = value
        self.reverse_map[value] = token

        return token

    def detokenize(self, token: str) -> Optional[str]:
        """
        Reverse tokenization.

        Args:
            token: Token string

        Returns:
            Original value or None
        """
        return self.token_map.get(token)

    def get_mapping(self) -> dict:
        """Get the token mapping."""
        return dict(self.token_map)


def hash_value(value: str, salt: str = None, algorithm: str = "sha256") -> str:
    """
    One-way hash transformation.

    Args:
        value: Original value
        salt: Optional salt for additional security
        algorithm: Hash algorithm (sha256, sha512, md5)

    Returns:
        Hashed value (truncated to 16 chars)
    """
    if salt:
        value = str(value) + salt

    if algorithm == "sha256":
        hash_obj = hashlib.sha256(value.encode())
    elif algorithm == "sha512":
        hash_obj = hashlib.sha512(value.encode())
    elif algorithm == "md5":
        hash_obj = hashlib.md5(value.encode())
    else:
        hash_obj = hashlib.sha256(value.encode())

    return hash_obj.hexdigest()[:16]

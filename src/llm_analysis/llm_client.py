"""LLM Analysis Module - OpenRouter Client"""

import logging
import os
import time
from typing import Any, Dict, List, Optional

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """LLM client for OpenRouter API."""

    DEFAULT_MODEL = "bytedance-seed/seed-1.6-flash"
    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize OpenRouter client.

        Args:
            api_key: OpenRouter API key
            model: Model name
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("LLM_MODEL", self.DEFAULT_MODEL)
        self.base_url = os.getenv("LLM_BASE_URL", self.BASE_URL)

        if not self.api_key:
            logger.warning("No OpenRouter API key provided. LLM features will be disabled.")

        self.client = None
        if OPENAI_AVAILABLE and self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=60.0)

        # Statistics
        self.request_count = 0
        self.token_usage = 0

    def is_available(self) -> bool:
        """Check if LLM client is available."""
        return self.client is not None

    def generate(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        system_prompt: str = None,
        retry: bool = True,
    ) -> str:
        """
        Generate text using OpenRouter API.

        Args:
            prompt: User prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            system_prompt: Optional system instructions
            retry: Whether to retry on failure

        Returns:
            Generated text
        """
        if not self.is_available():
            return "[LLM not available - API key not configured]"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        max_retries = 3 if retry else 1
        last_error = None

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model, messages=messages, temperature=temperature, max_tokens=max_tokens
                )

                # Update statistics
                self.request_count += 1
                if hasattr(response, "usage") and response.usage:
                    self.token_usage += response.usage.total_tokens

                return response.choices[0].message.content

            except Exception as e:
                last_error = e
                logger.warning(f"API error (attempt {attempt + 1}): {e}")

                if not retry:
                    break

                # Exponential backoff
                if attempt < max_retries - 1:
                    time.sleep(1.0 * (2**attempt))

        return f"[LLM Error: {last_error}]"

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "request_count": self.request_count,
            "total_tokens": self.token_usage,
            "average_tokens": self.token_usage / self.request_count if self.request_count > 0 else 0,
            "model": self.model,
            "available": self.is_available(),
        }

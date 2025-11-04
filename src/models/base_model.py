"""
🌙 Deamon Dev's Model Interface
Built with love by Deamon Dev 🚀

This module defines the base interface for all AI models.
"""

import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from termcolor import cprint


def safe_cprint(text, color):
    """Safe print that handles Unicode encoding issues"""
    try:
        cprint(text, color)
    except UnicodeEncodeError:
        # Remove emojis and special characters for Windows compatibility
        clean_text = (
            text.replace("✨", "")
            .replace("❌", "")
            .replace("🌙", "")
            .replace("🚀", "")
            .replace("⚡", "")
            .replace("💎", "")
            .replace("📈", "")
            .replace("📉", "")
            .replace("🌟", "")
            .replace("🤖", "")
            .replace("🔥", "")
            .replace("💰", "")
            .replace("⭐", "")
        )
        # Call cprint directly, not safe_cprint to avoid recursion
        cprint(clean_text, color)


@dataclass
class ModelResponse:
    """Standardized response format for all models"""

    content: str
    raw_response: Any  # Original response object
    model_name: str
    usage: Optional[Dict] = None


class BaseModel(ABC):
    """Base interface for all AI models"""

    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.client = None
        self._model_type = None  # Attribut privé avec underscore
        self.initialize_client(**kwargs)

    @property
    def model_type(self):
        """Return model type"""
        return self._model_type

    @abstractmethod
    def initialize_client(self, **kwargs) -> None:
        """Initialize the model's client"""
        pass

    def generate_response(
        self, system_prompt, user_content, temperature=0.7, max_tokens=None
    ):
        """Generate a response from the model with no caching"""
        try:
            # Add random nonce to prevent caching
            nonce = f"_{random.randint(1, 1000000)}"
            current_time = int(time.time())

            # Each request will be unique
            unique_content = f"{user_content}_{nonce}_{current_time}"

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": f"{system_prompt}_{current_time}"},
                    {"role": "user", "content": unique_content},
                ],
                temperature=temperature,
                max_tokens=max_tokens if max_tokens else self.max_tokens,
            )

            return response.choices[0].message

        except Exception as e:
            if "503" in str(e):
                raise e  # Let the retry logic handle 503s
            safe_cprint(f"❌ Model error: {str(e)}", "red")
            return None

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is available and properly configured"""
        pass

"""
🌙 Deamon Dev's Model Factory
Built with love by Deamon Dev
This module manages all available AI models and provides a unified interface.
"""

import os
import sys

# Force UTF-8 encoding for Windows compatibility
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="ignore")
    sys.stderr.reconfigure(encoding="utf-8", errors="ignore")
from pathlib import Path
from typing import Dict, Optional, Type

from dotenv import load_dotenv
from termcolor import cprint

from .base_model import BaseModel


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
            .replace("+-", "+")
            .replace("L-", "  ")
            .replace("🔑", "")
            .replace("═", "-")
        )
        # Remove all remaining non-ASCII characters
        clean_text = "".join(char for char in clean_text if ord(char) < 128)
        cprint(clean_text, color)


import random

from .claude_model import ClaudeModel
from .deepseek_model import DeepSeekModel
from .gemini_model import GeminiModel  # Re-enabled with Gemini 2.5 models
from .groq_model import GroqModel
from .ollama_model import OllamaModel
from .openai_model import OpenAIModel
from .xai_model import XAIModel
from .zai_model import ZAIModel  # Added Z.AI GLM-4.6 support


class ModelFactory:
    """Factory for creating and managing AI models"""

    # Map model types to their implementations
    MODEL_IMPLEMENTATIONS = {
        "claude": ClaudeModel,
        "groq": GroqModel,
        "openai": OpenAIModel,
        "gemini": GeminiModel,  # Re-enabled with Gemini 2.5 models
        "deepseek": DeepSeekModel,
        "ollama": OllamaModel,  # Add Ollama implementation
        "xai": XAIModel,  # xAI Grok models
        "zai": ZAIModel,  # Z.AI GLM-4.6 - Top Chinese model with Claude Sonnet 4 performance
    }

    # Default models for each type
    DEFAULT_MODELS = {
        "claude": "claude-3-5-haiku-latest",  # Latest fast Claude model
        "groq": "mixtral-8x7b-32768",  # Fast Mixtral model
        "openai": "gpt-4o",  # Latest GPT-4 Optimized
        "gemini": "gemini-2.5-flash",  # Fast Gemini 2.5 model
        "deepseek": "deepseek-reasoner",  # Enhanced reasoning model
        "ollama": "llama3.2",  # Meta's Llama 3.2 - balanced performance
        "xai": "grok-4-fast-reasoning",  # xAI's Grok 4 Fast with reasoning (best value: 2M context, cheap!)
        "zai": "glm-4.6",  # Z.AI GLM-4.6 - Latest model with Claude Sonnet 4 performance
    }

    def __init__(self):
        safe_cprint("\nCreating new ModelFactory instance...", "cyan")

        # Load environment variables first
        project_root = Path(__file__).parent.parent.parent
        env_path = project_root / ".env"
        safe_cprint(f"\nLoading environment from: {env_path}", "cyan")
        load_dotenv(dotenv_path=env_path)
        safe_cprint("Environment loaded", "green")

        self._models: Dict[str, BaseModel] = {}
        self._initialize_models()

    def _initialize_models(self):
        """Initialize all available models"""
        initialized = False

        safe_cprint("\nDeamon Dev's Model Factory Initialization", "cyan")
        safe_cprint("=" * 50, "cyan")

        # Debug current environment without exposing values
        safe_cprint("\n Environment Check:", "cyan")
        for key in [
            "GROQ_API_KEY",
            "OPENAI_KEY",
            "ANTHROPIC_KEY",
            "DEEPSEEK_KEY",
            "GROK_API_KEY",
            "GEMINI_KEY",
            "ZAI_API_KEY",
        ]:
            value = os.getenv(key)
            if value and len(value.strip()) > 0:
                safe_cprint(f"  +- {key}: Found ({len(value)} chars)", "green")
            else:
                safe_cprint(f"  +- {key}: Not found or empty", "red")

        # Try to initialize each model type
        for model_type, key_name in self._get_api_key_mapping().items():
            safe_cprint(f"\n Initializing {model_type} model...", "cyan")
            safe_cprint(f"  +- Looking for {key_name}...", "cyan")

            if api_key := os.getenv(key_name):
                try:
                    safe_cprint(
                        f"  +- Found {key_name} ({len(api_key)} chars)", "green"
                    )
                    safe_cprint(f"  +- Getting model class for {model_type}...", "cyan")

                    if model_type not in self.MODEL_IMPLEMENTATIONS:
                        safe_cprint(
                            f"  +-  Model type not found in implementations!", "red"
                        )
                        safe_cprint(
                            f"  L- Available implementations: {list(self.MODEL_IMPLEMENTATIONS.keys())}",
                            "yellow",
                        )
                        continue

                    model_class = self.MODEL_IMPLEMENTATIONS[model_type]
                    safe_cprint(
                        f"  +- Using model class: {model_class.__name__}", "cyan"
                    )

                    # Create instance with more detailed error handling
                    try:
                        safe_cprint(f"  +- Creating model instance...", "cyan")
                        safe_cprint(
                            f"  +- Default model name: {self.DEFAULT_MODELS[model_type]}",
                            "cyan",
                        )
                        model_instance = model_class(api_key)
                        safe_cprint(f"  +- Model instance created", "green")

                        # Test if instance is properly initialized
                        safe_cprint(f"  +- Testing model availability...", "cyan")
                        if model_instance.is_available():
                            self._models[model_type] = model_instance
                            initialized = True
                            safe_cprint(
                                f"  -  Successfully initialized {model_type}", "green"
                            )
                        else:
                            # For ZAI, don't show "not available" if it's just a plan issue
                            if model_type == "zai":
                                safe_cprint(
                                    f"  -  ZAI model configured but plan activation needed",
                                    "yellow",
                                )
                                safe_cprint(
                                    f"  -  Visit https://platform.z.ai/ to activate GLM Coding Lite",
                                    "cyan",
                                )
                            else:
                                safe_cprint(
                                    f"  -  Model instance created but not available",
                                    "yellow",
                                )
                    except Exception as instance_error:
                        safe_cprint(f"  +-  Error creating model instance", "yellow")
                        safe_cprint(
                            f"  +- Error type: {type(instance_error).__name__}",
                            "yellow",
                        )
                        safe_cprint(
                            f"  +- Error message: {str(instance_error)}", "yellow"
                        )
                        if hasattr(instance_error, "__traceback__"):
                            import traceback

                            safe_cprint(
                                f"    Traceback:\n{traceback.format_exc()}", "yellow"
                            )

                except Exception as e:
                    safe_cprint(
                        f"  +-  Failed to initialize {model_type} model", "yellow"
                    )
                    safe_cprint(f"  +- Error type: {type(e).__name__}", "yellow")
                    safe_cprint(f"  +- Error message: {str(e)}", "yellow")
                    if hasattr(e, "__traceback__"):
                        import traceback

                        safe_cprint(
                            f"    Traceback:\n{traceback.format_exc()}", "yellow"
                        )
            else:
                safe_cprint(f"  - {key_name} not found", "blue")

        # Initialize Ollama separately since it doesn't need an API key
        # Temporairement désactivé
        # try:
        #     safe_cprint("\n Initializing Ollama model...", "cyan")
        #     model_class = self.MODEL_IMPLEMENTATIONS["ollama"]
        #     model_instance = model_class(model_name=self.DEFAULT_MODELS["ollama"])
        #
        #     if model_instance.is_available():
        #         self._models["ollama"] = model_instance
        #         initialized = True
        #         safe_cprint(" Successfully initialized Ollama", "green")
        #     else:
        #         safe_cprint(" Ollama server not available - make sure 'ollama serve' is running", "yellow")
        # except Exception as e:
        #     safe_cprint(f" Failed to initialize Ollama: {str(e)}", "red")

        safe_cprint("\n" + "═" * 50, "cyan")
        safe_cprint(f"📊 Initialization Summary:", "cyan")
        safe_cprint(
            f"  +- Models attempted: {len(self._get_api_key_mapping())}", "cyan"
        )  # Ollama désactivé
        safe_cprint(f"  +- Models initialized: {len(self._models)}", "cyan")
        safe_cprint(f"  L- Available models: {list(self._models.keys())}", "cyan")

        if not initialized:
            safe_cprint(
                "\n No AI models available - check API keys and Ollama server", "yellow"
            )
            safe_cprint("Required environment variables:", "yellow")
            for model_type, key_name in self._get_api_key_mapping().items():
                safe_cprint(f"  +- {key_name} (for {model_type})", "yellow")
            safe_cprint("  L- Add these to your .env file 🌙", "yellow")
            safe_cprint("\nFor Ollama:", "yellow")
            safe_cprint("  L- Make sure 'ollama serve' is running", "yellow")
        else:
            # Print available models
            safe_cprint("\n🤖 Available AI Models:", "cyan")
            for model_type, model in self._models.items():
                safe_cprint(f"  +- {model_type}: {model.model_name}", "green")
            safe_cprint("  L- Deamon Dev's Model Factory Ready! 🌙", "green")

    def get_model(
        self, model_type: str, model_name: Optional[str] = None
    ) -> Optional[BaseModel]:
        """Get a specific model instance"""
        safe_cprint(
            f"\n Requesting model: {model_type} ({model_name or 'default'})", "cyan"
        )

        if model_type not in self.MODEL_IMPLEMENTATIONS:
            safe_cprint(f" Invalid model type: '{model_type}'", "red")
            safe_cprint("Available types:", "yellow")
            for available_type in self.MODEL_IMPLEMENTATIONS.keys():
                safe_cprint(f"  +- {available_type}", "yellow")
            return None

        if model_type not in self._models:
            key_name = self._get_api_key_mapping().get(model_type)
            if key_name:
                safe_cprint(
                    f" Model type '{model_type}' not available - check {key_name} in .env",
                    "red",
                )
            else:
                safe_cprint(f" Model type '{model_type}' not available", "red")
            return None

        model = self._models[model_type]
        if model_name and model.model_name != model_name:
            safe_cprint(
                f" Reinitializing {model_type} with model {model_name}...", "cyan"
            )
            try:
                # Special handling for Ollama models
                if model_type == "ollama":
                    model = self.MODEL_IMPLEMENTATIONS[model_type](
                        model_name=model_name
                    )
                else:
                    # For API-based models that need a key
                    if api_key := os.getenv(self._get_api_key_mapping()[model_type]):
                        model = self.MODEL_IMPLEMENTATIONS[model_type](
                            api_key, model_name=model_name
                        )
                    else:
                        safe_cprint(f" API key not found for {model_type}", "red")
                        return None

                self._models[model_type] = model
                safe_cprint(f" Successfully reinitialized with new model", "green")
            except Exception as e:
                safe_cprint(
                    f" Failed to initialize {model_type} with model {model_name}", "red"
                )
                safe_cprint(f" Error type: {type(e).__name__}", "red")
                safe_cprint(f" Error: {str(e)}", "red")
                return None

        return model

    def _get_api_key_mapping(self) -> Dict[str, str]:
        """Get mapping of model types to their API key environment variable names"""
        return {
            "claude": "ANTHROPIC_KEY",
            # "groq": "GROQ_API_KEY",  # Temporairement désactivé
            "openai": "OPENAI_KEY",
            "gemini": "GEMINI_KEY",  # Re-enabled with Gemini 2.5 models
            "deepseek": "DEEPSEEK_KEY",
            "xai": "GROK_API_KEY",  # Grok/xAI uses GROK_API_KEY
            "zai": "ZAI_API_KEY",  # Z.AI GLM-4.6 API key
            # Ollama doesn't need an API key as it runs locally
        }

    @property
    def available_models(self) -> Dict[str, list]:
        """Get all available models and their configurations"""
        return {
            model_type: model.AVAILABLE_MODELS
            for model_type, model in self._models.items()
        }

    def is_model_available(self, model_type: str) -> bool:
        """Check if a specific model type is available"""
        return model_type in self._models and self._models[model_type].is_available()

    def generate_response(
        self, system_prompt, user_content, temperature=0.7, max_tokens=None
    ):
        """Generate a response from the model with no caching"""
        try:
            # Add random nonce to prevent caching
            nonce = f"_{random.randint(1, 1000000)}"

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"{user_content}{nonce}",
                    },  # Add nonce to force new response
                ],
                temperature=temperature,
                max_tokens=max_tokens if max_tokens else self.max_tokens,
            )

            return response.choices[0].message

        except Exception as e:
            if "503" in str(e):
                raise e  # Let the retry logic handle 503s
            safe_cprint(f" Model error: {str(e)}", "red")
            return None


# Create a singleton instance
model_factory = ModelFactory()

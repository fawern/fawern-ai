"""
Base assistant class with flexible AI provider support.
"""

import os
from typing import AnyStr, Optional, Dict, Any
from .providers.provider_factory import ProviderFactory
from .config import get_provider_config, DEFAULT_PROVIDER

class BaseAssistant:
    """
    BaseAssistant serves as a base class for various assistant functionalities.
    Supports multiple AI providers (Groq, OpenAI, etc.) with flexible configuration.

    Attributes:
        provider_name (str): The AI provider to use (groq, openai, etc.)
        model (str): The model name used for generating completions.
        temperature (float): Sampling temperature for generating responses.
        max_tokens (int): Maximum number of tokens for generating responses.
        top_p (float): Controls diversity via nucleus sampling.
    """

    def __init__(self, 
                 provider_name: str = None,
                 model: str = None, 
                 temperature: float = 0.5, 
                 max_tokens: int = 1000, 
                 top_p: float = 1.0,
                 **kwargs):
        """
        Initializes the BaseAssistant class with flexible AI provider support.

        Args:
            provider_name (str): AI provider name (groq, openai, etc.)
            model (str): The model name for generating responses.
            temperature (float): The sampling temperature.
            max_tokens (int): The maximum number of tokens.
            top_p (float): The nucleus sampling value.
            **kwargs: Additional provider-specific arguments
        """
        self.provider_name = provider_name or DEFAULT_PROVIDER
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.kwargs = kwargs
        
        self.provider_config = get_provider_config(self.provider_name)
        
        if not self.model:
            self.model = self.provider_config.get("default_model")
        
        self._provider = None
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the AI provider."""
        try:
            self._provider = ProviderFactory.get_provider(
                provider_name=self.provider_name,
                model=self.model,
                **self.kwargs
            )
        except Exception as e:
            available_providers = ProviderFactory.get_available_providers()
            raise ValueError(
                f"Failed to initialize provider '{self.provider_name}': {e}. "
                f"Available providers: {available_providers}"
            )
    
    def _get_completion(self, prompt: str, **kwargs) -> AnyStr:
        """
        Internal method to generate a completion response based on the provided prompt.

        Args:
            prompt (str): The input prompt for generating a completion.
            **kwargs: Additional arguments for the completion

        Returns:
            str: The generated completion response.
        """
        completion_kwargs = {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            **kwargs
        }
        
        try:
            return self._provider.get_completion(prompt, **completion_kwargs)
        except Exception as e:
            raise Exception(f"AI completion error ({self.provider_name}): {e}")
    
    def _get_streaming_completion(self, prompt: str, **kwargs):
        """
        Internal method to generate a streaming completion response.

        Args:
            prompt (str): The input prompt for generating a completion.
            **kwargs: Additional arguments for the completion

        Yields:
            str: Chunks of the generated response.
        """
        completion_kwargs = {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            **kwargs
        }
        
        try:
            for chunk in self._provider.get_streaming_completion(prompt, **completion_kwargs):
                yield chunk
        except Exception as e:
            raise Exception(f"AI streaming completion error ({self.provider_name}): {e}")
    
    def switch_provider(self, provider_name: str, **kwargs):
        """
        Switch to a different AI provider.

        Args:
            provider_name (str): New provider name
            **kwargs: Additional provider-specific arguments
        """
        self.provider_name = provider_name
        self.kwargs.update(kwargs)
        self._initialize_provider()
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the current provider.

        Returns:
            Dict containing provider information
        """
        return {
            "provider_name": self.provider_name,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "config": self.provider_config
        }
    
    def validate_provider(self) -> bool:
        """
        Validate that the current provider is working.

        Returns:
            bool: True if provider is valid
        """
        return ProviderFactory.validate_provider(self.provider_name)
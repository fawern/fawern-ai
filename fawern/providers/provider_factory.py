"""
Provider factory for creating AI provider instances.
"""

from .base_provider import BaseProvider
from .groq_provider import GroqProvider
from .openai_provider import OpenAIProvider
from ..config import get_provider_config, get_available_providers

class ProviderFactory:
    """
    Factory class for creating AI provider instances.
    """
    
    _providers = {
        "groq": GroqProvider,
        "openai": OpenAIProvider,
    }
    
    @classmethod
    def get_provider(cls, provider_name: str = None, **kwargs) -> BaseProvider:
        """
        Get an AI provider instance.
        
        Args:
            provider_name (str): Name of the provider (groq, openai, etc.)
            **kwargs: Additional arguments for the provider
            
        Returns:
            BaseProvider: Provider instance
        """
        config = get_provider_config(provider_name)
        provider_name = provider_name or config.get("provider", "groq")
        
        if provider_name not in cls._providers:
            available = list(cls._providers.keys())
            raise ValueError(f"Unknown provider: {provider_name}. Available: {available}")
        
        provider_class = cls._providers[provider_name]
        
        model = kwargs.pop("model", config.get("default_model"))
        
        return provider_class(
            api_key=config["api_key"],
            model=model,
            **kwargs
        )
    
    @classmethod
    def get_available_providers(cls) -> list:
        """
        Get list of available providers.
        
        Returns:
            list: Available provider names
        """
        return list(cls._providers.keys())
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """
        Register a new provider.
        
        Args:
            name (str): Provider name
            provider_class (type): Provider class
        """
        if not issubclass(provider_class, BaseProvider):
            raise ValueError("Provider class must inherit from BaseProvider")
        
        cls._providers[name] = provider_class
    
    @classmethod
    def validate_provider(cls, provider_name: str) -> bool:
        """
        Validate that a provider is available and has valid credentials.
        
        Args:
            provider_name (str): Provider name
            
        Returns:
            bool: True if provider is valid
        """
        try:
            provider = cls.get_provider(provider_name)
            return provider.validate_credentials()
        except Exception:
            return False

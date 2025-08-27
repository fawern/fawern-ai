"""
Base provider class for AI services.
"""

from abc import ABC, abstractmethod
from typing import Any

class BaseProvider(ABC):
    """
    Abstract base class for AI providers.
    All AI providers must implement this interface.
    """
    
    def __init__(self, api_key: str, model: str = None, **kwargs):
        """
        Initialize the provider.
        
        Args:
            api_key (str): API key for the provider
            model (str): Model name to use
            **kwargs: Additional provider-specific arguments
        """
        self.api_key = api_key
        self.model = model
        self.kwargs = kwargs
        self._client = None
    
    @abstractmethod
    def get_completion(self, prompt: str, **kwargs) -> str:
        """
        Get a completion from the AI provider.
        
        Args:
            prompt (str): The input prompt
            **kwargs: Additional arguments for the completion
            
        Returns:
            str: The generated response
        """
        pass
    
    @abstractmethod
    def get_streaming_completion(self, prompt: str, **kwargs):
        """
        Get a streaming completion from the AI provider.
        
        Args:
            prompt (str): The input prompt
            **kwargs: Additional arguments for the completion
            
        Yields:
            str: Chunks of the generated response
        """
        pass
    
    @property
    @abstractmethod
    def client(self):
        """Get the underlying client object."""
        pass
    
    @abstractmethod
    def validate_credentials(self) -> bool:
        """
        Validate that the API credentials are working.
        
        Returns:
            bool: True if credentials are valid
        """
        pass

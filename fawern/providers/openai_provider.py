"""
OpenAI provider implementation.
"""

from .base_provider import BaseProvider

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class OpenAIProvider(BaseProvider):
    """
    OpenAI provider implementation.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4", **kwargs):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key (str): OpenAI API key
            model (str): Model name (default: gpt-4)
            **kwargs: Additional arguments
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed. Run: pip install openai")
        
        super().__init__(api_key, model, **kwargs)
        self._client = OpenAI(api_key=api_key)
    
    @property
    def client(self):
        """Get the OpenAI client."""
        return self._client
    
    def get_completion(self, prompt: str, **kwargs) -> str:
        """
        Get a completion from OpenAI.
        
        Args:
            prompt (str): The input prompt
            **kwargs: Additional arguments (temperature, max_tokens, etc.)
            
        Returns:
            str: The generated response
        """
        params = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.5),
            "max_tokens": kwargs.get("max_tokens", 1000),
            "top_p": kwargs.get("top_p", 1.0),
            "stream": False,
        }
        
        params.update(kwargs)
        
        try:
            completion = self._client.chat.completions.create(**params)
            return completion.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")
    
    def get_streaming_completion(self, prompt: str, **kwargs):
        """
        Get a streaming completion from OpenAI.
        
        Args:
            prompt (str): The input prompt
            **kwargs: Additional arguments
            
        Yields:
            str: Chunks of the generated response
        """
        params = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.5),
            "max_tokens": kwargs.get("max_tokens", 1000),
            "top_p": kwargs.get("top_p", 1.0),
            "stream": True,
        }
        
        params.update(kwargs)
        
        try:
            completion = self._client.chat.completions.create(**params)
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")
    
    def validate_credentials(self) -> bool:
        """
        Validate OpenAI API credentials.
        
        Returns:
            bool: True if credentials are valid
        """
        try:
            test_response = self.get_completion("Hello", max_tokens=5)
            return True
        except Exception:
            return False

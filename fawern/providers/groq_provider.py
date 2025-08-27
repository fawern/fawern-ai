"""
Groq AI provider implementation.
"""

from .base_provider import BaseProvider

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

class GroqProvider(BaseProvider):
    """
    Groq AI provider implementation.
    """
    
    def __init__(self, api_key: str, model: str = "llama-3.1-70b-versatile", **kwargs):
        """
        Initialize Groq provider.
        
        Args:
            api_key (str): Groq API key
            model (str): Model name (default: llama-3.1-70b-versatile)
            **kwargs: Additional arguments
        """
        if not GROQ_AVAILABLE:
            raise ImportError("Groq library not installed. Run: pip install groq")
        
        super().__init__(api_key, model, **kwargs)
        self._client = Groq(api_key=api_key)
    
    @property
    def client(self):
        """Get the Groq client."""
        return self._client
    
    def get_completion(self, prompt: str, **kwargs) -> str:
        """
        Get a completion from Groq.
        
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
            raise Exception(f"Groq API error: {e}")
    
    def get_streaming_completion(self, prompt: str, **kwargs):
        """
        Get a streaming completion from Groq.
        
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
            raise Exception(f"Groq API error: {e}")
    
    def validate_credentials(self) -> bool:
        """
        Validate Groq API credentials.
        
        Returns:
            bool: True if credentials are valid
        """
        try:
            self.get_completion("Hello", max_tokens=5)
            return True
        except Exception:
            return False

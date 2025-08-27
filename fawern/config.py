import os
from dotenv import load_dotenv
import yaml
from typing import Dict, Any, Optional

load_dotenv()

AI_PROVIDERS = {
    "groq": {
        "api_key_env": "GROQ_API_KEY",
        "default_model": "llama-3.1-70b-versatile",
        "base_url": "https://api.groq.com/openai/v1",
        "client_class": "GroqClient"
    },
    "openai": {
        "api_key_env": "OPENAI_API_KEY", 
        "default_model": "gpt-4",
        "base_url": "https://api.openai.com/v1",
        "client_class": "OpenAIClient"
    }
}

DEFAULT_PROVIDER = os.getenv("FAWERN_AI_PROVIDER", "groq")

API_KEYS = {}
for provider, config in AI_PROVIDERS.items():
    api_key = os.getenv(config["api_key_env"])
    if api_key:
        API_KEYS[provider] = api_key

if DEFAULT_PROVIDER not in API_KEYS:
    available_providers = list(API_KEYS.keys())
    if available_providers:
        DEFAULT_PROVIDER = available_providers[0]
    else:
        raise ValueError(f"No AI provider API keys found. Please set one of: {list(AI_PROVIDERS.keys())}")

os.environ[AI_PROVIDERS[DEFAULT_PROVIDER]["api_key_env"]] = API_KEYS[DEFAULT_PROVIDER]

PROMPTS_FILE = "prompts.yaml"
    
def load_prompts(file_name=PROMPTS_FILE):
    possible_paths = [
        file_name,
        os.path.join(os.path.dirname(__file__), file_name), 
        os.path.join(os.path.dirname(os.path.dirname(__file__)), file_name),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts.yaml"),
    ]
    
    for path in possible_paths:
        try:
            with open(path, "r", encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            continue
    
    raise Exception(f"Prompts file '{file_name}' not found in any of these locations: {possible_paths}")

def get_provider_config(provider: str = None) -> Dict[str, Any]:
    """
    Get configuration for a specific AI provider.
    
    Args:
        provider (str): Provider name (groq, openai, etc.)
        
    Returns:
        Dict containing provider configuration
    """
    provider = provider or DEFAULT_PROVIDER
    if provider not in AI_PROVIDERS:
        raise ValueError(f"Unknown provider: {provider}. Available: {list(AI_PROVIDERS.keys())}")
    
    config = AI_PROVIDERS[provider].copy()
    config["api_key"] = API_KEYS.get(provider)
    
    if not config["api_key"]:
        raise ValueError(f"API key not found for provider: {provider}")
    
    return config

def get_available_providers() -> list:
    return list(API_KEYS.keys())

PROMPTS = load_prompts()

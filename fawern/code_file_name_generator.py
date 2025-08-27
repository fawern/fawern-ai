from .base_assistant import BaseAssistant
import os
from .get_code_from_input import get_code_from_input
from .config import PROMPTS
from typing import Dict, Any

class CodeFileNameGenerator(BaseAssistant):
    """
    CodeFileNameGenerator is a utility class for generating meaningful file names based on Python code content.
    """

    def __init__(self, 
                 provider_name: str = None,
                 model: str = None, 
                 temperature: float = 0.7, 
                 max_tokens: int = 50, 
                 top_p: float = 1.0,
                 **kwargs):
        """
        Initializes the CodeFileNameGenerator class with model, temperature, max_tokens, and top_p attributes.
        """
        super().__init__(provider_name, model, temperature, max_tokens, top_p, **kwargs)
        self.prompts: Dict[str, Any] = PROMPTS["prompts"]

    def generate_file_name(self, code):
        """
        Generates a meaningful file name based on the provided Python code.

        Args:
            code (str): The Python code from which to generate a file name.

        Returns:
            str: A file name that reflects the primary functionality of the code.
        """
        code = get_code_from_input(code)

        prompt_template: str = self.prompts["CodeFileNameGenerator"]["generate_file_name"]["prompt"]
        prompt: str = prompt_template.format(code=code)

        file_name = self._get_completion(prompt)
        file_name = file_name.strip().split("\n")[0].strip().replace(" ", "_").replace('"', '').replace("'", '')

        return file_name

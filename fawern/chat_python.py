import os
import subprocess
import sys
import re

from .base_assistant import BaseAssistant
from .save_to_md import save_generated_data_to_md
from .code_file_name_generator import CodeFileNameGenerator
from .get_code_from_input import get_code_from_input

from .config import PROMPTS

from typing import Dict, Optional, List, Any, Match


class ChatPython(BaseAssistant):
    """
    ChatPython is an AI Python developer that generates Python code based on a given input prompt.
    """

    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    def __init__(self, 
                 provider_name: str = None,
                 model: str = None, 
                 temperature: float = 0.5, 
                 max_tokens: int = 1000, 
                 top_p: float = 1.0,
                 **kwargs) -> None:
        super().__init__(provider_name, model, temperature, max_tokens, top_p, **kwargs)
        self.generated_code: str = ''
        self.prompt: str = ''
        self.file_name: str = ''
        self.root_directory: str = os.getcwd()
        self.prompts: Dict[str, Any] = PROMPTS["prompts"]



    def _print_progress_bar(self, message: str, bar_width: int = 30):
        bar = f"{self.GREEN}[{'=' * bar_width}]{self.RESET}"
        print(f"{self.BOLD}{message}{self.RESET} {bar}")

    def generate_code(
            self, 
            prompt_input: str, 
            write_code_to_file: bool = True, 
            run_code: bool = True,
            cleanup_installed_module: bool = True, 
            cleanup_generated_file: bool = True
    ) -> str:

        if not write_code_to_file:
            run_code = False

        base_prompt: str = self.prompts["ChatPython"]["generate_code"]["prompt"]
        self.prompt: str = base_prompt.format(prompt=prompt_input)

        self._print_progress_bar(f"{self.YELLOW}Generating code from prompt...{self.RESET}")
        self.generated_code: str = self._get_completion(self.prompt)
        self.generated_code: str = self._remove_python_prefix(self.generated_code)
        print(f"{self.GREEN}✓ Code generation completed.{self.RESET}")

        if run_code:
            self._write_code_to_file()
            output = self._run_generated_code(cleanup_installed_module)
            if cleanup_generated_file:
                generated_file_path: str = os.path.join(self.root_directory, self.file_name)
                try:
                    os.remove(generated_file_path)
                    print(f"{self.YELLOW}🧹 Generated file '{self.file_name}' deleted successfully.{self.RESET}")
                except Exception as e:
                    print(f"{self.RED}⚠ Warning: Could not delete generated file '{self.file_name}': {e}{self.RESET}")
            return output if output else self.generated_code

        return self.generated_code

    def _remove_python_prefix(self, code: str) -> str:

        prefix: str = "python"
        code: str = code.replace("`", '')
        lines: List[str] = code.splitlines()
        try:
            if lines and lines[0].strip().startswith(prefix):
                lines[0] = lines[0].strip()[len(prefix):].strip()
                return "\n".join(lines)
            else:
                return code
        except Exception as e:
            raise Exception(f"Try again, {e}")

    def _generate_file_name(self) -> str:

        prompt_for_file_name: str = (
            f"Based on the provided Python code description, generate a meaningful and contextually appropriate file "
            f"name that ends with '.py'. The file name should reflect the primary functionality of the code. Here is "
            f"the input: {self.prompt}"
        )
        generated_file_name: str = self._get_completion(prompt_for_file_name)
        generated_file_name: str = generated_file_name.strip().split("\n")[0].strip().replace("", "").replace('"', '')
        return generated_file_name

    def _write_code_to_file(self) -> None:
        path: str = ""
        self.file_name: str = self._generate_file_name()
        try:
            full_path: str = os.path.join(self.root_directory, path)
            os.makedirs(full_path, exist_ok=True)
            saved_path: str = os.path.join(full_path, self.file_name)
            self._print_progress_bar(f"{self.BLUE}Writing code to {saved_path}{self.RESET}")
        except Exception as e:
            raise Exception(f"{self.RED}Cannot create directory: {e}{self.RESET}")

        if self.generated_code:
            with open(saved_path, "w") as file:
                file.write(self.generated_code)
            print(f"{self.GREEN}✓ Code written to {self.file_name}{self.RESET}")
        else:
            raise Exception(f"{self.RED}No code generated yet{self.RESET}")


    def _run_generated_code(self, cleanup_installed_module) -> Optional[str]:
        full_path: str = os.path.join(self.root_directory, self.file_name)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"{self.RED}Error: The file {full_path} does not exist!{self.RESET}")
        
        self._print_progress_bar(f"{self.YELLOW}Running script {self.BLUE}{full_path}{self.RESET}")

        installed_module: Optional[str] = None
        try:
            result: subprocess.CompletedProcess = subprocess.run([sys.executable, full_path], capture_output=True, text=True)
            if result.returncode != 0:
                if "ModuleNotFoundError" in result.stderr:
                    match: Optional[Match] = re.search(r"No module named '([^']+)'", result.stderr)
                    if match:
                        missing_module: str = match.group(1)
                        print(f"{self.YELLOW}Module '{missing_module}' not found. Installing...{self.RESET}")
                        install_result: subprocess.CompletedProcess = subprocess.run(
                            [sys.executable, "-m", "pip", "install", missing_module],
                            capture_output=True,
                            text=True
                        )
                        if install_result.returncode == 0:
                            print(f"{self.GREEN}Module '{missing_module}' installed. Re-running script...{self.RESET}")
                            result = subprocess.run([sys.executable, full_path], capture_output=True, text=True)
                            if result.returncode != 0:
                                raise Exception(f"{self.RED}Error after installing {missing_module}:{self.RESET}\n{result.stderr}")
                            if cleanup_installed_module:
                                print(f"{self.YELLOW}Cleaning up '{missing_module}'...{self.RESET}")
                                uninstall_result: subprocess.CompletedProcess = subprocess.run(
                                    [sys.executable, "-m", "pip", "uninstall", missing_module, "-y"],
                                    capture_output=True,
                                    text=True
                                )
                                if uninstall_result.returncode == 0:
                                    print(f"{self.GREEN}Uninstalled '{missing_module}'{self.RESET}")
                                else:
                                    print(f"{self.RED}Failed to uninstall '{missing_module}':\n{uninstall_result.stderr}{self.RESET}")
                            return result.stdout
                        else:
                            raise Exception(f"{self.RED}Failed to install '{missing_module}':\n{install_result.stderr}{self.RESET}")
                raise Exception(f"{self.RED}Script error:\n{result.stderr}{self.RESET}")
            print(f"{self.GREEN}Script executed successfully!{self.RESET}")
            return result.stdout
        except Exception as e:
            raise Exception(f"{self.RED}Cannot run code: {e}{self.RESET}")


class CodeAnalyzer(BaseAssistant):


    def __init__(self) -> None:

        super().__init__()
        self.prompts: Dict[str, Any] = PROMPTS["prompts"]

    def analyze_code(self, code: str) -> str:
        code: str = get_code_from_input(code)
        prompt_template: str = self.prompts["CodeAnalyzer"]["analyze_code"]["prompt"]
        prompt: str = prompt_template.format(code=code)
        generated_code: str = self._get_completion(prompt)
        file_name_generator: CodeFileNameGenerator = CodeFileNameGenerator()
        file_name: str = file_name_generator.generate_file_name(code)
        save_generated_data_to_md(file_name, generated_code)
        return generated_code

    def find_syntax_errors(self, code: str) -> str:
        code: str = get_code_from_input(code)
        prompt_template: str = self.prompts["CodeAnalyzer"]["find_syntax_errors"]["prompt"]
        prompt: str = prompt_template.format(code=code)
        generated_code: str = self._get_completion(prompt)
        file_name_generator: CodeFileNameGenerator = CodeFileNameGenerator()
        file_name: str = file_name_generator.generate_file_name(code)
        save_generated_data_to_md(file_name, generated_code)
        return generated_code

    def suggest_optimizations(self, code: str) -> str:
        code: str = get_code_from_input(code)
        prompt_template: str = self.prompts["CodeAnalyzer"]["suggest_optimizations"]["prompt"]
        prompt: str = prompt_template.format(code=code)
        generated_code: str = self._get_completion(prompt)
        file_name_generator: CodeFileNameGenerator = CodeFileNameGenerator()
        file_name: str = file_name_generator.generate_file_name(code)
        save_generated_data_to_md(file_name, generated_code)
        return generated_code

    def refactor_code(self, code: str) -> str:
        code: str = get_code_from_input(code)
        prompt_template: str = self.prompts["CodeAnalyzer"]["refactor_code"]["prompt"]
        prompt: str = prompt_template.format(code=code)
        generated_code: str = self._get_completion(prompt)
        file_name_generator: CodeFileNameGenerator = CodeFileNameGenerator()
        file_name: str = file_name_generator.generate_file_name(code)
        save_generated_data_to_md(file_name, generated_code)
        return generated_code

    def get_code_explanation(self, code: str) -> str:
        code: str = get_code_from_input(code)
        prompt_template: str = self.prompts["CodeAnalyzer"]["get_code_explanation"]["prompt"]
        prompt: str = prompt_template.format(code=code)
        generated_code: str = self._get_completion(prompt)
        file_name_generator: CodeFileNameGenerator = CodeFileNameGenerator()
        file_name: str = file_name_generator.generate_file_name(code)
        save_generated_data_to_md(file_name, generated_code)
        return generated_code

    def fix_code(self, code: str) -> str:
        code: str = get_code_from_input(code)
        prompt_template: str = self.prompts["CodeAnalyzer"]["fix_code"]["prompt"]
        prompt: str = prompt_template.format(code=code)
        generated_code: str = self._get_completion(prompt)
        file_name_generator: CodeFileNameGenerator = CodeFileNameGenerator()
        file_name: str = file_name_generator.generate_file_name(code)
        save_generated_data_to_md(file_name, generated_code)
        return generated_code

    def find_errors(self, code: str) -> str:
        code: str = get_code_from_input(code)
        prompt_template: str = self.prompts["CodeAnalyzer"]["find_errors"]["prompt"]
        prompt: str = prompt_template.format(code=code)
        generated_code: str = self._get_completion(prompt)
        file_name_generator: CodeFileNameGenerator = CodeFileNameGenerator()
        file_name: str = file_name_generator.generate_file_name(code)
        save_generated_data_to_md(file_name, generated_code)
        return generated_code

    def suggest_improvements(self, code: str) -> str:
        code: str = get_code_from_input(code)
        prompt_template: str = self.prompts["CodeAnalyzer"]["suggest_improvements"]["prompt"]
        prompt: str = prompt_template.format(code=code)
        generated_code: str = self._get_completion(prompt)
        file_name_generator: CodeFileNameGenerator = CodeFileNameGenerator()
        file_name: str = file_name_generator.generate_file_name(code)
        save_generated_data_to_md(file_name, generated_code)
        return generated_code

    def check_security_issues(self, code: str) -> str:
        code: str = get_code_from_input(code)
        prompt_template: str = self.prompts["CodeAnalyzer"]["check_security_issues"]["prompt"]
        prompt: str = prompt_template.format(code=code)
        generated_code: str = self._get_completion(prompt)
        file_name_generator: CodeFileNameGenerator = CodeFileNameGenerator()
        file_name: str = file_name_generator.generate_file_name(code)
        save_generated_data_to_md(file_name, generated_code)
        return generated_code

    def generate_test_cases(self, code: str) -> str:
        code: str = get_code_from_input(code)
        prompt_template: str = self.prompts["CodeAnalyzer"]["generate_test_cases"]["prompt"]
        prompt: str = prompt_template.format(code=code)
        generated_code: str = self._get_completion(prompt)
        file_name_generator: CodeFileNameGenerator = CodeFileNameGenerator()
        file_name: str = file_name_generator.generate_file_name(code)
        save_generated_data_to_md(file_name, generated_code)
        return generated_code


class CodeFormatter(BaseAssistant):
    """
    CodeFormatter formats Python code according to PEP8 standards.
    """

    def __init__(self) -> None:
        super().__init__()
        self.prompts: Dict[str, Any] = PROMPTS["prompts"]

    def format_code(self, code: str) -> str:
        code: str = get_code_from_input(code)
        prompt_template: str = self.prompts["CodeFormatter"]["format_code"]["prompt"]
        prompt: str = prompt_template.format(code=code)
        generated_code: str = self._get_completion(prompt)
        file_name_generator: CodeFileNameGenerator = CodeFileNameGenerator()
        file_name: str = file_name_generator.generate_file_name(code)
        save_generated_data_to_md(file_name, generated_code)
        return generated_code


class ErrorLogAnalyzer(BaseAssistant):
    """
    ErrorLogAnalyzer logs and analyzes Python errors, providing suggestions for fixing them.
    """

    def __init__(self) -> None:
        super().__init__()
        self.prompts: Dict[str, Any] = PROMPTS["prompts"]
        self.error_logs: List[str] = []

    def analyze_errors(self, error_message: str) -> str:
        prompt_template: str = self.prompts["ErrorLogAnalyzer"]["analyze_errors"]["prompt"]
        prompt: str = prompt_template.format(error_message=error_message)
        generated_code: str = self._get_completion(prompt)
        file_name_generator: CodeFileNameGenerator = CodeFileNameGenerator()
        file_name: str = file_name_generator.generate_file_name(error_message)
        save_generated_data_to_md(file_name, generated_code)
        return generated_code


class CodeReviewer(BaseAssistant):
    """
    CodeReviewer provides functionality to review Python code and provide feedback on its structure, clarity, and overall quality.
    """

    def __init__(self) -> None:
        super().__init__()
        self.prompts: Dict[str, Any] = PROMPTS["prompts"]

    def review_code(self, code: str) -> str:
        code: str = get_code_from_input(code)
        prompt_template: str = self.prompts["CodeReviewer"]["review_code"]["prompt"]
        prompt: str = prompt_template.format(code=code)
        generated_code: str = self._get_completion(prompt)
        file_name_generator: CodeFileNameGenerator = CodeFileNameGenerator()
        file_name: str = file_name_generator.generate_file_name(code)
        save_generated_data_to_md(file_name, generated_code)
        return generated_code


class DocumentationGenerator(BaseAssistant):
    """
    DocumentationGenerator generates detailed docstrings and inline comments for Python code.
    """

    def __init__(self) -> None:
        super().__init__()
        self.prompts: Dict[str, Any] = PROMPTS["prompts"]

    def generate_docstrings(self, code: str) -> str:
        code: str = get_code_from_input(code)
        prompt_template: str = self.prompts["DocumentationGenerator"]["generate_docstrings"]["prompt"]
        prompt: str = prompt_template.format(code=code)
        generated_code: str = self._get_completion(prompt)
        file_name_generator: CodeFileNameGenerator = CodeFileNameGenerator()
        file_name: str = file_name_generator.generate_file_name(code)
        save_generated_data_to_md(file_name, generated_code)
        return generated_code



class ConvertToPython(BaseAssistant):
    """
    ConvertToPython converts code from other languages to Python code.
    """

    def __init__(self) -> None:
        super().__init__()
        self.prompts: Dict[str, Any] = PROMPTS["prompts"]

    def convert_code(self, code: str) -> str:
        prompt_template: str = self.prompts["ConvertToPython"]["convert_code"]["prompt"]
        prompt: str = prompt_template.format(code=code)
        generated_code: str = self._get_completion(prompt)
        file_name_generator: CodeFileNameGenerator = CodeFileNameGenerator()
        file_name: str = file_name_generator.generate_file_name(code)
        save_generated_data_to_md(file_name, generated_code)
        return generated_code


class CodeVisualizer(BaseAssistant):
    """
    CodeVisualizer generates visual representations, such as flowcharts or class diagrams, for Python code.
    """

    def __init__(self) -> None:
        super().__init__()
        self.prompts: Dict[str, Any] = PROMPTS["prompts"]

    def visualize_code(self, code: str) -> str:
        code: str = get_code_from_input(code)
        prompt_template: str = self.prompts["CodeVisualizer"]["visualize_code"]["prompt"]
        prompt: str = prompt_template.format(code=code)
        generated_code: str = self._get_completion(prompt)
        file_name_generator: CodeFileNameGenerator = CodeFileNameGenerator()
        file_name: str = file_name_generator.generate_file_name(code)
        save_generated_data_to_md(file_name, generated_code)
        return generated_code


class BugFixer(BaseAssistant):
    """
    BugFixer automatically identifies and fixes bugs in Python code.
    """

    def __init__(self) -> None:
        super().__init__()
        self.prompts: Dict[str, Any] = PROMPTS["prompts"]

    def fix_bugs(self, code: str) -> str:
        code: str = get_code_from_input(code)
        prompt_template: str = self.prompts["BugFixer"]["fix_bugs"]["prompt"]
        prompt: str = prompt_template.format(code=code)
        generated_code: str = self._get_completion(prompt)
        file_name_generator: CodeFileNameGenerator = CodeFileNameGenerator()
        file_name: str = file_name_generator.generate_file_name(code)
        save_generated_data_to_md(file_name, generated_code)
        return generated_code



class UnitTestGenerator(BaseAssistant):
    """
    UnitTestGenerator generates unit tests for Python code.
    """

    def __init__(self) -> None:
        super().__init__()
        self.prompts: Dict[str, Any] = PROMPTS["prompts"]

    def generate_tests(self, code: str) -> str:
        code: str = get_code_from_input(code)
        prompt_template: str = self.prompts["UnitTestGenerator"]["generate_tests"]["prompt"]
        prompt: str = prompt_template.format(code=code)
        generated_code: str = self._get_completion(prompt)
        file_name_generator: CodeFileNameGenerator = CodeFileNameGenerator()
        file_name: str = file_name_generator.generate_file_name(code)
        save_generated_data_to_md(file_name, generated_code)
        return generated_code
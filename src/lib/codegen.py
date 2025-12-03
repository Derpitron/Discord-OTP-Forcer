from regex_string_generator import generate_string

from .types import CodeMode


def generate_random_code(codeMode: CodeMode) -> str:
    return generate_string(codeMode.pattern)

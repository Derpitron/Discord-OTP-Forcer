from regex_string_generator import generate_string

from .types import CodeMode


# TODO: handle accepting custom regex pattern in config parsing
def generate_random_code(codeMode: CodeMode) -> str:
    return generate_string(codeMode.pattern)

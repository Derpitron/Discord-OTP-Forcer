def color(string: str, color: str) -> str:
    color_code_map = {
        "red": "\033[31m",
        "yellow": "\033[33m",
        "green": "\033[32m",
        "cyan": "\033[96m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "black": "\033[30m",
        "white": "\033[37m",
        "custom": "\033[0;34;47m",
    }
    if color not in color_code_map:
        raise ValueError("Invalid ANSI color code choice.")

    return f"{color_code_map[color]}{string}\033[0m"

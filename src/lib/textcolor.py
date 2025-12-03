from enum import Enum


class Color(str, Enum):
    Black = "\033[30m"
    Red = "\033[31m"
    Green = "\033[32m"
    Yellow = "\033[33m"
    Blue = "\033[34m"
    Magenta = "\033[35m"
    Cyan = "\033[36m"
    White = "\033[37m"
    Reset = "\033[0m"


def color(string: str, color: Color) -> str:
    return f"{color.value}{string}{Color.Reset.value}"

from .types import Color


def color(string: str, color: Color) -> str:
    return f"{color.value}{string}{Color.Reset.value}"

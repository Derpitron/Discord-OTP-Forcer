from secrets import choice as randchoice
from string import ascii_lowercase as letters
from string import digits


def list_to_string(l: list) -> str:
    return "".join(map(str, l))


def generate_random_character(character_set: str) -> str:
    yield randchoice(character_set)


def generate_random_code(mode: str) -> str:
    match mode:
        case "normal":
            return list_to_string(
                list(next(generate_random_character(digits)) for _ in range(6))
            )
        case "backup":
            return list_to_string(
                list(
                    next(generate_random_character(letters + digits)) for _ in range(8)
                )
            )
        case "backup_let":
            return list_to_string(
                list(next(generate_random_character(letters)) for _ in range(8))
            )
        case "both":
            return randchoice(
                [generate_random_code("normal"), generate_random_code("backup")]
            )

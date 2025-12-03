from typing import TypeVar


class UserCausedHalt(Exception):
    pass


T = TypeVar("T")


# TODO: This is ugly
def unwrap(x: T | None) -> T:
    if x is None:
        raise TypeError("Expected actual variable, got None")
    return x

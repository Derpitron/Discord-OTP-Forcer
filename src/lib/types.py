from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple, TypeVar

"""
This is the canonical definition for program and account configuration. all possibilities defined here

Naming convention here:

PascalCase for classes, types, kinds, enum-possibilities
camelCase for objects, variables, instances, members
"""

# TODO: add proper user documentation
# TODO: update contributors and thanks list

T = TypeVar("T")


def unwrap(x: T | None) -> T:
    if x is None:
        raise TypeError("Expected actual variable, got None")
    return x


class ProgramMode(Enum):
    Login = 0
    Reset = 1


@dataclass
class CodeMode:
    pattern: str


# TODO: make this readonly
@dataclass
class CodeMode_Normal(CodeMode):
    pattern: str = r"\d{6}"


@dataclass
class CodeMode_Backup(CodeMode):
    # TODO: investigate 9-11 char backup codes and implement here if they exist now
    pattern: str = r"[a-z0-9]{8}"


class Browser(Enum):
    Chrome = 0
    # TODO: IMPLEMENT
    # Chromium = 1
    # Firefox = 2


@dataclass(frozen=True)
class ProgramConfig:
    """
    This is public and can be shared anywhere.
    """

    programMode: ProgramMode
    codeMode: CodeMode
    browser: Browser

    sensitiveDebug: bool
    logCreation: bool
    headless: bool
    logLevel: str
    elementLoadTolerance: float


@dataclass(frozen=True)
class AccountConfig:
    """
    I want this to be private and shared as little as possible.
    """

    email: str
    password: str

    newPassword: str
    resetToken: str

    authToken: str


@dataclass(frozen=True)
class Config:
    program: ProgramConfig
    account: AccountConfig


@dataclass
class SessionStats:
    attemptedCodeCount: int  # The number of codes attempted in this session
    # fmt: off
    attemptedBackupCodeCount: int # The number of backup codes attempted in this session
    # fmt: on
    ratelimitCount: int  # The number of times I got ratelimited
    slowDownCount: int  # The number of times the submit button loaded too slowly, because of a server-side invisible ratelimit or network conditions.
    elapsedTimeSeconds: float  # The time this program ran, in seconds


class CodeError(Enum):
    Invalid = 0
    Ratelimited = 1

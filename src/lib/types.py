from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple

from selenium.webdriver.remote.webdriver import WebDriver as Driver
from selenium.webdriver.remote.webelement import WebElement as Element

"""
This is the canonical definition for program and account configuration. all possibilities defined here

Naming convention here:

PascalCase for classes, types, kinds, enum-possibilities
camelCase for objects, variables, instances, members
"""


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
    pattern: str = r"[a-z0-9]{8}"


class Browser(Enum):
    Chrome = 0
    # TODO: IMPLEMENT
    # Chromium = 1
    # Firefox = 2


class ProgramConfig(NamedTuple):
    """
    This is public and can be shared anywhere.
    """

    programMode: ProgramMode
    codeMode: CodeMode
    browser: Browser

    sensitiveDebug: bool
    logCreation: bool
    headless: bool


class AccountConfig(NamedTuple):
    """
    I want this to be private and shared as little as possible.
    """

    email: str
    password: str

    newPassword: str
    resetToken: str

    authToken: str


class Config(NamedTuple):
    program: ProgramConfig
    account: AccountConfig


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


@dataclass
class LoginFields:
    password: Element
    code: Element
    email: Element


@dataclass
class SessionStats:
    attemptedCodeCount: int
    ratelimitCount: int
    slowDownCount: int
    elapsedTime: float


class CodeInputResult(Enum):
    Success = 0
    Err_Invalid = 1
    Err_RateLimited = 2

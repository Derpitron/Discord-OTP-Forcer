from dataclasses import dataclass
from enum import Enum, StrEnum
from typing import TypeVar, TypedDict, NewType
from selenium.webdriver.remote.webdriver import WebDriver

"""
This is the canonical definition for program and account configuration. all possibilities defined here

Naming convention here:

PascalCase for classes, types, kinds, enum-possibilities
camelCase for objects, variables, instances, members
"""

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


@dataclass
class CodeMode_Normal(CodeMode):
    pattern: str = r"\d{6}"


@dataclass
class CodeMode_Backup(CodeMode):
    pattern: str = r"[a-z0-9]{8}"


class Browser(StrEnum):
    # SeleniumBase uses Chrome as default for "chrome",
    # if not, uses Chromium it seems.
    Chrome = "chrome"
    Chromium = "chromium"
    Brave = "brave"
    # Imposible for the moment to implement as this program
    # uses CDP commands and undetected-chromedriver
    # Firefox = "firefox"


@dataclass(frozen=True)
class ProgramConfig:
    """
    This is public and can be shared anywhere.
    """

    programMode: ProgramMode
    codeMode: CodeMode
    browser: Browser

    checkUpdates: bool
    sensitiveDebug: bool
    logCreation: bool
    headless: bool
    logLevel: str
    elementLoadTolerance: float

    usualAttemptDelayRange: tuple[int, int]
    ratelimitedAttemptDelayRange: tuple[int, int]


class CensoredStr(str):
    def __repr__(self) -> str:
        return "'******'"


@dataclass(frozen=True)
class AccountConfig:
    """
    I want this to be private and shared as little as possible.
    """

    email: str | CensoredStr
    password: str | CensoredStr

    newPassword: str | CensoredStr
    resetToken: str | CensoredStr

    authToken: str | CensoredStr


@dataclass(frozen=True)
class Config:
    program: ProgramConfig
    account: AccountConfig


@dataclass(frozen=True)
class BrowserSession:
    driver: WebDriver
    config: Config


class ProgramConfigDict(TypedDict):
    """
    Raw YAML structure for program configuration.
    """

    programMode: str
    codeMode: str
    browser: str
    checkUpdates: bool
    headless: bool
    logCreation: bool
    sensitiveDebug: bool
    logLevel: str
    elementLoadTolerance: float
    usualAttemptDelayMin: int
    usualAttemptDelayMax: int
    ratelimitedAttemptDelayMin: int
    ratelimitedAttemptDelayMax: int


@dataclass
class SessionStats:
    attemptedCodeCount: int  # The number of codes attempted in this session
    attemptedBackupCodeCount: int  # The number of backup codes attempted in this session
    ratelimitCount: int  # The number of times I got ratelimited
    slowDownCount: int  # The number of times the submit button loaded too slowly, because of a server-side invisible ratelimit or network conditions.
    serviceUnavailableCount: int  # The number of times discord was unavailable.
    elapsedTimeSeconds: float  # The time this program ran, in seconds


@dataclass(frozen=True)
class InvalidCode:
    attempted_code: str
    raw_message: str


@dataclass(frozen=True)
class RateLimited:
    raw_message: str


@dataclass(frozen=True)
class ServiceUnavailable:
    raw_message: str


@dataclass(frozen=True)
class TokenExpired:
    raw_message: str


@dataclass(frozen=True)
class UnknownError:
    raw_message: str


@dataclass(frozen=True)
class NetworkOffline:
    raw_message: str


CodeError = InvalidCode | RateLimited | ServiceUnavailable | TokenExpired | UnknownError | NetworkOffline


@dataclass(frozen=True)
class TomlNotFound:
    pass


@dataclass(frozen=True)
class TomlParseError:
    pass


@dataclass(frozen=True)
class NetworkError:
    reason: str


VersionCheckError = TomlNotFound | TomlParseError | NetworkError

LocalVersion = NewType("LocalVersion", str)
GitHubVersion = NewType("GitHubVersion", str)

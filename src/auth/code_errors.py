from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By, ByType
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..lib.types import (
    CodeStatusFound,
    CodeStatusNotFound,
    CodeStatusResult,
    CodeError,
    InvalidCode,
    RateLimited,
    ServiceUnavailable,
    TokenExpired,
    UnknownError,
    NetworkOffline,
)


_CODE_STATUS_FALLBACK_XPATHS: frozenset[str] = frozenset(
    {
        "//form//div[text()='Invalid two-factor code']",
        "//form//div[text()='The resource is being ratelimited.']",
        "//form//div[text()='Service resource is being rate-limited.']",
        "//form//div[text()='Service resource is being rate limited.']",
        "//form//div[text()='The resource is being rate limited.']",
    }
)

_RATE_LIMIT_MESSAGES: frozenset[str] = frozenset(
    {
        "The resource is being ratelimited.",
        "Service resource is being rate-limited.",
        "Service resource is being rate limited.",
        "You are being rate limited.",
        "The resource is being rate limited.",
    }
)

_SERVICE_UNAVAILABLE_MESSAGES: frozenset[str] = frozenset(
    {
        "POST /auth/mfa/totp [503]",
        "503: Service Unavailable",
    }
)


def get_code_status(
    driver: WebDriver,
    wait: WebDriverWait,
    code_status_element: tuple[ByType, str],
) -> CodeStatusResult:
    # Try first with the Code Status Element Class, if not, fallback to the raw text message
    try:
        wait.until(EC.visibility_of_element_located(code_status_element))
        return CodeStatusFound(
            message=driver.find_element(*code_status_element).text,
            used_fallback=False,
        )
    except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
        pass

    combined_xpath = " | ".join(_CODE_STATUS_FALLBACK_XPATHS)
    try:
        return CodeStatusFound(
            message=driver.find_element(By.XPATH, combined_xpath).text,
            used_fallback=True,
        )
    except NoSuchElementException:
        pass

    return CodeStatusNotFound()


def parse_code_error(raw_message: str, attempted_code: str) -> CodeError:
    match raw_message:
        case "Invalid two-factor code":
            return InvalidCode(attempted_code=attempted_code, raw_message=raw_message)
        case msg if msg in _RATE_LIMIT_MESSAGES:
            return RateLimited(raw_message=raw_message)
        case "POST /auth/reset [400]":
            return TokenExpired(raw_message=raw_message)
        case msg if msg in _SERVICE_UNAVAILABLE_MESSAGES:
            return ServiceUnavailable(raw_message=raw_message)
        case msg if "the network is offline" in msg:
            return NetworkOffline(raw_message=raw_message)
        case _:
            return UnknownError(raw_message=raw_message)

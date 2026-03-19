from ..lib.types import (
    CodeError,
    InvalidCode,
    RateLimited,
    ServiceUnavailable,
    TokenExpired,
    UnknownError,
    NetworkOffline,
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


def parse_code_error(raw_message: str, attempted_code: str) -> CodeError:
    match raw_message:
        case "Invalid two-factor code":
            return InvalidCode(attempted_code=attempted_code, raw_message=raw_message)
        case msg if msg in _RATE_LIMIT_MESSAGES:
            return RateLimited(raw_message=raw_message)
        case "POST /auth/reset [400]":
            return TokenExpired(raw_message=raw_message)
        case "POST /auth/mfa/totp [503]":
            return ServiceUnavailable(raw_message=raw_message)
        case msg if "the network is offline" in msg:
            return NetworkOffline(raw_message=raw_message)
        case _:
            return UnknownError(raw_message=raw_message)

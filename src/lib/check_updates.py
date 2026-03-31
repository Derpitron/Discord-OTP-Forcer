import json
from loguru import logger
import requests

from .types import (
    LocalVersion,
    GitHubVersion,
    VersionCheckError,
    TomlNotFound,
    TomlParseError,
    NetworkError,
)

_session = requests.Session()
_session.headers["User-Agent"] = "Discord-OTP-Forcer"


def _fetch_url(url: str) -> str | NetworkError:
    """
    Makes a GET request to the given URL and returns the content as text.
    Returns None if the request fails.
    """
    try:
        response = _session.get(url, timeout=5)
        response.raise_for_status()
        return response.text
    except requests.RequestException as error:
        return NetworkError(reason=str(error))


def _fetch_json(url: str) -> dict | NetworkError:
    """
    Makes a GET request to the given URL git _fetch_url and returns the content as json format.
    Returns None if the request fails or the json decoder failed to parse the content.
    """
    content = _fetch_url(url)
    if isinstance(content, NetworkError):
        return content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return NetworkError(reason=f"Failed to parse JSON response from {url}")


def _extract_version_from_toml(lines: list[str]) -> str | TomlParseError:
    """
    Extracts the version string from a pyproject.toml file.
    (Version is in the third line, index 2)
    eg: 'version = "1.2.3"' -> '"1.2.3"'
    """
    try:
        version: str = lines[2].split('"')[1]
        return version
    except IndexError:
        return TomlParseError()


def _parse_version(version: str) -> list[int]:
    """
    Splits a version string into a list of integers.
    eg: "1.2.3" -> [1, 2, 3].
    """
    return [int(part) for part in version.split(".")]


def _get_local_version() -> LocalVersion | VersionCheckError:
    """
    Reads the local version of the program directly from the local file of pyproject.toml.
    """
    try:
        with open("pyproject.toml", encoding="utf-8") as file:
            extracted_version: str | TomlParseError = _extract_version_from_toml(file.readlines())

            if isinstance(extracted_version, TomlParseError):
                return extracted_version

            return LocalVersion(extracted_version)
    except FileNotFoundError:
        return TomlNotFound()


def _fetch_github_version() -> GitHubVersion | VersionCheckError:
    """
    Fetches the remote pyproject.toml from GitHub and extracts the version.
    """
    content = _fetch_url("https://codeberg.org/Discord-OTP-Forcer/Discord-OTP-Forcer/raw/branch/main/pyproject.toml")
    if isinstance(content, NetworkError):
        return content

    extracted_version: str | TomlParseError = _extract_version_from_toml(content.splitlines())
    if isinstance(extracted_version, TomlParseError):
        return extracted_version

    return GitHubVersion(extracted_version)


def _fetch_latest_commit_hash() -> str | None:
    """
    Fetches the latest commit hash from the main branch on GitHub.
    """
    # Maybe not broken? need to be tested
    data = _fetch_json("https://codeberg.org/api/v1/repos/Discord-OTP-Forcer/Discord-OTP-Forcer/git/refs/heads/main")
    if isinstance(data, NetworkError):
        return None

    commit_hash = data.get("object", {}).get("sha", "")
    return commit_hash[:7] if commit_hash else None


def _log_version_error(error: VersionCheckError, source: str) -> None:
    match error:
        case TomlNotFound():
            logger.debug(f"Could not find pyproject.toml ({source} source).")
        case TomlParseError():
            logger.debug(f"Could not parse version from pyproject.toml ({source} source).")
        case NetworkError(reason=r):
            logger.debug(f"Network error reading {source} version: {r}")


def check_for_updates() -> None:
    """
    Compares the local version against the latest GitHub version and logs the result.
    """
    local_version = _get_local_version()
    if isinstance(local_version, (TomlNotFound, TomlParseError, NetworkError)):
        _log_version_error(local_version, "local")
        return

    github_version = _fetch_github_version()
    if isinstance(github_version, (TomlNotFound, TomlParseError, NetworkError)):
        _log_version_error(github_version, "GitHub")
        return

    local = _parse_version(local_version)
    github = _parse_version(github_version)

    # github > local  → 1 - 0 =  1  (github is newer)
    # github < local  → 0 - 1 = -1  (local is newer)
    # github == local → 0 - 0 =  0  (same version)
    result = (github > local) - (github < local)

    match result:
        case 1:
            logger.warning(f"New version available: {github_version} (Current: {local_version})")
            if commit_hash := _fetch_latest_commit_hash():
                logger.warning(f"Latest commit on main: {commit_hash}")
        case -1:
            logger.info(f"Local version {local_version} is ahead of GitHub: {github_version}")
        case 0:
            logger.info(f"You are on the latest version: {local_version}")

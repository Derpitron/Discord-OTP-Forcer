import json
from loguru import logger

import requests
from .types import LocalVersion, GitHubVersion


_session = requests.Session()
_session.headers["User-Agent"] = "Discord-OTP-Forcer"


def _fetch_url(url: str) -> str | None:
    """
    Makes a GET request to the given URL and returns the content as text.
    Returns None if the request fails.
    """
    try:
        response = _session.get(url, timeout=5)
        response.raise_for_status()
        return response.text
    except requests.RequestException as error:
        logger.debug(f"Request to {url} failed: {error}")
        return None


def _fetch_json(url: str) -> dict | None:
    """
    Makes a GET request to the given URL git _fetch_url and returns the content as json format.
    Returns None if the request fails or the json decoder failed to parse the content.
    """
    content = _fetch_url(url)
    if content is None:
        return None
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        logger.debug(f"Failed to parse JSON response from {url}")
        return None


def _extract_version_from_toml(lines: list[str]) -> str | None:
    """
    Extracts the version string from a pyproject.toml file.
    (Version is in the third line, index 2)
    eg: 'version = "1.2.3"' -> '"1.2.3"'
    """
    try:
        version: str = lines[2].split('"')[1]
        return version
    except IndexError:
        logger.debug("Could not parse version from pyproject.toml.")


def _parse_version(version: str) -> list[int]:
    """
    Splits a version string into a list of integers.
    eg: "1.2.3" -> [1, 2, 3].
    """
    return [int(part) for part in version.split(".")]


def _get_local_version() -> LocalVersion | None:
    """
    Reads the local version of the program directly from the local file of pyproject.toml.
    """
    try:
        with open("pyproject.toml", encoding="utf-8") as file:
            extracted_version: str | None = _extract_version_from_toml(file.readlines())

            return LocalVersion(extracted_version) if extracted_version is not None else None
    except FileNotFoundError:
        logger.debug("Could not find pyproject.toml.")
        return None


def _fetch_github_version() -> GitHubVersion | None:
    """
    Fetches the remote pyproject.toml from GitHub and extracts the version.
    """
    content = _fetch_url("https://raw.githubusercontent.com/Derpitron/Discord-OTP-Forcer/refs/heads/main/pyproject.toml")
    if content is None:
        return None

    extracted_version: str | None = _extract_version_from_toml(content.splitlines())

    return GitHubVersion(extracted_version) if extracted_version is not None else None


def _fetch_latest_commit_hash() -> str | None:
    """
    Fetches the latest commit hash from the main branch on GitHub.
    """
    data = _fetch_json("https://api.github.com/repos/Derpitron/Discord-OTP-Forcer/git/ref/heads/main")
    if data is None:
        return None

    commit_hash = data.get("object", {}).get("sha", "")
    return commit_hash[:7] if commit_hash else None


def check_for_updates() -> None:
    """
    Compares the local version against the latest GitHub version and logs the result.
    """
    local_version = _get_local_version()
    if local_version is None:
        logger.debug("Could not retrieve the local version.")
        return

    github_version = _fetch_github_version()
    if github_version is None:
        logger.debug("Could not retrieve the version from GitHub.")
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
            commit_hash = _fetch_latest_commit_hash()
            if commit_hash:
                logger.warning(f"Latest commit on main: {commit_hash}")
        case -1:
            logger.info(f"Local version {local_version} is ahead of GitHub: {github_version}")
        case 0:
            logger.info(f"You are on the latest version: {local_version}")

from platform import system
from src.lib.types import BinaryPath
from .binary_finder import find_binary, build_linux_candidates, build_macos_candidates, build_windows_candidates
from seleniumbase.fixtures import constants as sb_constants

_BINARIES_WINDOWS: list[str] = ["chrome.exe", "chromium.exe"]
_BINARIES_LINUX: list[str] = ["chromium", "chromium-browser"]
_BINARIES_MACOS: list[str] = ["Chromium"]


def register_chromium_browser() -> None:
    match system():
        case "Windows":
            sb_constants.ValidBinaries.valid_chrome_binaries_on_windows.extend(_BINARIES_WINDOWS)
        case "Linux":
            sb_constants.ValidBinaries.valid_chrome_binaries_on_linux.extend(_BINARIES_LINUX)
        case "Darwin":
            sb_constants.ValidBinaries.valid_chrome_binaries_on_macos.extend(_BINARIES_MACOS)


def find_chromium_binary() -> BinaryPath:
    fallback_names: list[str]
    candidate_paths: list[BinaryPath]
    match system():
        case "Windows":
            candidate_paths = build_windows_candidates("Chromium", _BINARIES_WINDOWS)
            fallback_names = _BINARIES_WINDOWS
        case "Linux":
            candidate_paths = build_linux_candidates("chromium", _BINARIES_LINUX)
            fallback_names = _BINARIES_LINUX
        case "Darwin":
            candidate_paths = build_macos_candidates("Chromium", _BINARIES_MACOS)
            fallback_names = _BINARIES_MACOS
        case _:
            candidate_paths = []
            fallback_names = []
    return find_binary("Chromium", candidate_paths, fallback_names)

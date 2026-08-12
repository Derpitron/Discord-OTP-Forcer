from platform import system

from seleniumbase.fixtures import constants as sb_constants

from src.lib.types import BinaryPath

from .binary_finder import build_linux_candidates, build_macos_candidates, build_windows_candidates, find_binary

_BINARIES_WINDOWS: list[str] = ["thorium.exe", "thorium-browser.exe"]
_BINARIES_LINUX: list[str] = ["thorium-browser", "thorium"]
_BINARIES_MACOS: list[str] = ["Thorium", "Thorium Browser"]
_THORIUM_MACOS_APPS = ["Thorium", "Alex313031-Thorium"]


def register_thorium_browser() -> None:
    match system():
        case "Windows":
            sb_constants.ValidBinaries.valid_chrome_binaries_on_windows.extend(_BINARIES_WINDOWS)
        case "Linux":
            sb_constants.ValidBinaries.valid_chrome_binaries_on_linux.extend(_BINARIES_LINUX)
        case "Darwin":
            sb_constants.ValidBinaries.valid_chrome_binaries_on_macos.extend(_BINARIES_MACOS)


def find_thorium_binary() -> BinaryPath:
    fallback_names: list[str]
    candidate_paths: list[BinaryPath]
    match system():
        case "Windows":
            candidate_paths = build_windows_candidates("Thorium", _BINARIES_WINDOWS)
            fallback_names = _BINARIES_WINDOWS
        case "Linux":
            candidate_paths = build_linux_candidates("thorium", _BINARIES_LINUX)
            fallback_names = _BINARIES_LINUX
        case "Darwin":
            candidate_paths = build_macos_candidates("Thorium", _THORIUM_MACOS_APPS)
            fallback_names = _BINARIES_MACOS
        case _:
            candidate_paths = []
            fallback_names = []
    return find_binary("Thorium", candidate_paths, fallback_names)

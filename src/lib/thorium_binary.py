from pathlib import Path
from platform import system
from seleniumbase.fixtures import constants as sb_constants

from .types import BinaryPath


_THORIUM_BINARIES_WINDOWS: list[str] = ["thorium.exe", "thorium-browser.exe"]
_THORIUM_BINARIES_LINUX: list[str] = ["thorium-browser", "thorium"]
_THORIUM_BINARIES_MACOS: list[str] = ["Thorium", "Thorium Browser"]


def register_thorium_browser() -> None:
    match system():
        case "Windows":
            sb_constants.ValidBinaries.valid_chrome_binaries_on_windows.extend(_THORIUM_BINARIES_WINDOWS)
        case "Linux":
            sb_constants.ValidBinaries.valid_chrome_binaries_on_linux.extend(_THORIUM_BINARIES_LINUX)
        case "Darwin":
            sb_constants.ValidBinaries.valid_chrome_binaries_on_macos.extend(_THORIUM_BINARIES_MACOS)


def find_thorium_binary() -> BinaryPath:
    """
    Locate the Thorium browser executable for the current OS.
    """
    candidate_paths: list[BinaryPath] = []

    match system():
        case "Windows":
            from os import environ

            local_appdata = environ.get("LOCALAPPDATA", "")
            program_files = environ.get("PROGRAMFILES", "C:\\Program Files")
            program_files_x86 = environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)")
            candidate_paths = [
                BinaryPath(rf"{local_appdata}\Thorium\Application\thorium.exe"),
                BinaryPath(rf"{program_files}\Thorium\Application\thorium.exe"),
                BinaryPath(rf"{program_files_x86}\Thorium\Application\thorium.exe"),
            ]
        case "Linux":
            candidate_paths = [
                BinaryPath("/usr/bin/thorium-browser"),
                BinaryPath("/usr/local/bin/thorium-browser"),
                BinaryPath("/opt/thorium/thorium-browser"),
            ]
        case "Darwin":
            home = Path.home()
            candidate_paths = [
                BinaryPath("/Applications/Thorium.app/Contents/MacOS/Thorium"),
                BinaryPath("/Applications/Alex313031-Thorium.app/Contents/MacOS/Thorium"),
                BinaryPath(str(home / "Applications/Thorium.app/Contents/MacOS/Thorium")),
                BinaryPath(str(home / "Applications/Alex313031-Thorium.app/Contents/MacOS/Thorium")),
            ]

    for path in candidate_paths:
        if Path(path).is_file():
            return path

    # Fallback
    from shutil import which

    found_in_path = which("thorium-browser") or which("thorium")
    if found_in_path:
        return BinaryPath(found_in_path)

    raise FileNotFoundError("Thorium binary not found. Make sure Thorium is installed correctly.")

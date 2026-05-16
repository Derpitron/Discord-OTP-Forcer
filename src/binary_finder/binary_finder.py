from pathlib import Path
from shutil import which
from src.lib.types import BinaryPath
from os import environ


def build_windows_candidates(
    app_folder: str,
    binary_names: list[str],
) -> list[BinaryPath]:
    local_appdata: str = environ.get("LOCALAPPDATA", "")
    program_files: str = environ.get("PROGRAMFILES", r"C:\Program Files")
    program_files_x86: str = environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")
    base_dirs: list[str] = [local_appdata, program_files, program_files_x86]
    paths: list[BinaryPath] = [BinaryPath(rf"{dir}\{app_folder}\Application\{name}") for dir in base_dirs for name in binary_names]
    return paths


def build_linux_candidates(opt_subdir: str, binary_names: list[str]) -> list[BinaryPath]:
    base_dirs: list[str] = ["/usr/bin", "/usr/local/bin"]
    paths: list[BinaryPath] = [BinaryPath(f"{dir}/{name}") for dir in base_dirs for name in binary_names]
    paths += [BinaryPath(f"/opt/{opt_subdir}/{name}") for name in binary_names]
    return paths


def build_macos_candidates(executable: str, app_names: list[str]) -> list[BinaryPath]:
    home: Path = Path.home()
    base_dirs: list[str] = ["/Applications", str(home / "Applications")]
    paths: list[BinaryPath] = [BinaryPath(f"{dir}/{app}.app/Contents/MacOS/{executable}") for dir in base_dirs for app in app_names]
    return paths


def find_binary(
    name: str,
    candidate_paths: list[BinaryPath],
    fallback_names: list[str],
) -> BinaryPath:
    """Search if the binary exist in the candidate and fallback paths"""
    for path in candidate_paths:
        if Path(path).is_file():
            return path
    for fallback in fallback_names:
        if found := which(fallback):
            return BinaryPath(found)
    raise FileNotFoundError(f"{name} binary not found. Make sure {name} is installed correctly.")

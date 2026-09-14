"""ZIP archive primitives used by the source-only release manager."""

from __future__ import annotations

import shutil
import stat
import zipfile
from collections.abc import Callable, Container
from pathlib import Path


def zip_runtime(
    source: Path,
    destination: Path,
    *,
    validate_tree: Callable[[Path], None],
    ignored_names: Container[str],
) -> None:
    """Write a deterministic, symlink-free Runtime archive."""
    validate_tree(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source.rglob("*")):
            relative = path.relative_to(source)
            if any(part in ignored_names for part in relative.parts):
                continue
            if path.is_dir():
                continue
            info = zipfile.ZipInfo(relative.as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (path.stat().st_mode & 0o777) << 16
            archive.writestr(info, path.read_bytes())


def write_backup_archive(
    source: Path,
    destination: Path,
    *,
    validate_tree: Callable[[Path], None],
) -> None:
    """Write a managed Runtime tree archive without following symlinks."""
    validate_tree(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(source.rglob("*")):
            if path.is_dir():
                continue
            relative = path.relative_to(source)
            info = zipfile.ZipInfo(relative.as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (path.stat().st_mode & 0o777) << 16
            archive.writestr(info, path.read_bytes())


def zip_entries(archive_path: Path) -> list[str]:
    try:
        with zipfile.ZipFile(archive_path) as archive:
            return archive.namelist()
    except (OSError, zipfile.BadZipFile) as error:
        raise ValueError(f"release package is not a valid ZIP: {archive_path.name}") from error


def validate_zip_member(name: str) -> None:
    path = Path(name)
    if not name or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"release package contains an unsafe path: {name}")


def archive_current_release(archive_path: Path) -> str:
    try:
        with zipfile.ZipFile(archive_path) as archive:
            info = archive.getinfo(".mpa-version")
            for line in archive.read(info).decode("utf-8").splitlines():
                if line.startswith("current_release:"):
                    return line.split(":", 1)[1].strip()
    except (KeyError, UnicodeDecodeError, OSError, zipfile.BadZipFile) as error:
        raise ValueError("release package .mpa-version is invalid") from error
    raise ValueError("release package current_release is missing")


def extract_runtime(
    archive_path: Path,
    destination: Path,
    *,
    validate_member: Callable[[str], None],
) -> None:
    destination.mkdir(parents=True, exist_ok=False)
    names: set[str] = set()
    try:
        with zipfile.ZipFile(archive_path) as archive:
            for info in archive.infolist():
                validate_member(info.filename)
                if info.filename in names:
                    raise ValueError(f"release package contains a duplicate path: {info.filename}")
                names.add(info.filename)
                mode = (info.external_attr >> 16) & 0xFFFF
                kind = stat.S_IFMT(mode)
                if kind == stat.S_IFLNK:
                    raise ValueError(f"release package contains a symlink: {info.filename}")
                if kind not in (0, stat.S_IFREG, stat.S_IFDIR):
                    raise ValueError(f"release package contains an unsupported file type: {info.filename}")
                if info.is_dir() and kind not in (0, stat.S_IFDIR):
                    raise ValueError(f"release package directory has an invalid type: {info.filename}")
                if not info.is_dir() and kind == stat.S_IFDIR:
                    raise ValueError(f"release package file has an invalid type: {info.filename}")
                target = (destination / info.filename).resolve()
                if destination.resolve() not in target.parents and target != destination.resolve():
                    raise ValueError(f"release package path escapes staging: {info.filename}")
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)
                permissions = (info.external_attr >> 16) & 0o777
                if permissions:
                    target.chmod(permissions)
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        shutil.rmtree(destination, ignore_errors=True)
        raise ValueError("release package extraction failed") from error

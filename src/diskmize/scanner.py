"""Disk traversal primitives.

Every public function is cancellable through a ``threading.Event`` so the UI
can stop a long scan without killing the process, and every filesystem error is
collected instead of silently swallowed.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from threading import Event
from typing import Iterable

MAX_ERRORS_KEPT = 100


class ScanCancelledError(Exception):
    """Raised when the caller requested to stop an in-progress scan."""


@dataclass(frozen=True)
class FileEntry:
    path: Path
    size: int
    modified: float | None = None

    @property
    def name(self) -> str:
        return self.path.name


@dataclass(frozen=True)
class FolderEntry:
    path: Path
    size: int

    @property
    def name(self) -> str:
        return self.path.name


@dataclass
class ScanResult:
    entries: list = field(default_factory=list)
    errors: list[tuple[str, str]] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return len(self.errors)


def _check_stop(stop_event: Event | None) -> None:
    if stop_event is not None and stop_event.is_set():
        raise ScanCancelledError("scan cancelled by user")


def _record(errors: list[tuple[str, str]], path: str, exc: OSError) -> None:
    if len(errors) < MAX_ERRORS_KEPT:
        errors.append((path, exc.__class__.__name__))


def directory_size(
    root: str | os.PathLike[str],
    *,
    stop_event: Event | None = None,
    errors: list[tuple[str, str]] | None = None,
) -> int:
    """Total size in bytes of *root*, without following symlinks."""
    total = 0
    stack = [os.fspath(root)]
    while stack:
        _check_stop(stop_event)
        current = stack.pop()
        try:
            with os.scandir(current) as iterator:
                for entry in iterator:
                    try:
                        if entry.is_symlink():
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(entry.path)
                        elif entry.is_file(follow_symlinks=False):
                            total += entry.stat(follow_symlinks=False).st_size
                    except OSError as exc:
                        if errors is not None:
                            _record(errors, entry.path, exc)
        except OSError as exc:
            if errors is not None:
                _record(errors, current, exc)
    return total


def scan_files(
    root: str | os.PathLike[str], *, stop_event: Event | None = None, min_size: int = 0
) -> ScanResult:
    """Walk *root* recursively and return every regular file with its size."""
    result = ScanResult()
    for current, dirs, files in os.walk(os.fspath(root), followlinks=False):
        _check_stop(stop_event)
        for name in files:
            _check_stop(stop_event)
            path = Path(current) / name
            try:
                if path.is_symlink():
                    continue
                stat = path.stat()
            except OSError as exc:
                _record(result.errors, str(path), exc)
                continue
            if stat.st_size < min_size:
                continue
            result.entries.append(FileEntry(path=path, size=stat.st_size, modified=stat.st_mtime))
    return result


def largest_files(
    root: str | os.PathLike[str], *, limit: int = 100, stop_event: Event | None = None
) -> ScanResult:
    """Convenience wrapper: scan and keep the *limit* biggest files."""
    if limit <= 0:
        raise ValueError("limit must be positive")
    result = scan_files(root, stop_event=stop_event)
    result.entries.sort(key=lambda item: item.size, reverse=True)
    del result.entries[limit:]
    return result


def scan_top_level_folders(
    root: str | os.PathLike[str], *, stop_event: Event | None = None
) -> ScanResult:
    """Size of each immediate sub-directory of *root* (non-recursive listing)."""
    result = ScanResult()
    try:
        with os.scandir(os.fspath(root)) as iterator:
            entries = list(iterator)
    except OSError as exc:
        _record(result.errors, os.fspath(root), exc)
        return result

    for entry in entries:
        _check_stop(stop_event)
        try:
            if entry.is_symlink() or not entry.is_dir(follow_symlinks=False):
                continue
        except OSError as exc:
            _record(result.errors, entry.path, exc)
            continue
        size = directory_size(entry.path, stop_event=stop_event, errors=result.errors)
        result.entries.append(FolderEntry(path=Path(entry.path), size=size))
    return result


def top_folders(
    root: str | os.PathLike[str], *, limit: int = 100, stop_event: Event | None = None
) -> ScanResult:
    if limit <= 0:
        raise ValueError("limit must be positive")
    result = scan_top_level_folders(root, stop_event=stop_event)
    result.entries.sort(key=lambda item: item.size, reverse=True)
    del result.entries[limit:]
    return result


def total_size(paths: Iterable[Path]) -> int:
    total = 0
    for path in paths:
        try:
            total += path.stat().st_size
        except OSError:
            continue
    return total

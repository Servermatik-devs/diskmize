"""Guarded file deletion.

DiskMize is a disk cleanup tool, so deletion is a core feature, but it must be
narrow and predictable: only regular files, never directories, never symlinks,
never a recursive delete.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass
class DeleteOutcome:
    deleted: list[Path] = field(default_factory=list)
    errors: list[tuple[str, str]] = field(default_factory=list)
    skipped: list[tuple[str, str]] = field(default_factory=list)

    @property
    def deleted_count(self) -> int:
        return len(self.deleted)

    @property
    def freed_bytes(self) -> int:
        return sum(size for _, size in self._sizes)

    _sizes: list[tuple[str, int]] = field(default_factory=list, repr=False)


def _why_not_deletable(path: Path) -> str | None:
    try:
        if path.is_symlink():
            return "symlink"
        if path.is_dir():
            return "directory"
        if not path.exists():
            return "missing"
        if not path.is_file():
            return "not a regular file"
    except OSError as exc:
        return exc.__class__.__name__
    return None


def delete_files(paths: Iterable[str | os.PathLike[str]]) -> DeleteOutcome:
    """Delete the given regular files, reporting every refusal and failure."""
    outcome = DeleteOutcome()
    for raw in paths:
        path = Path(raw)
        reason = _why_not_deletable(path)
        if reason is not None:
            outcome.skipped.append((str(path), reason))
            continue
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        try:
            os.remove(path)
        except OSError as exc:
            outcome.errors.append((str(path), exc.__class__.__name__))
            continue
        outcome.deleted.append(path)
        outcome._sizes.append((str(path), size))
    return outcome

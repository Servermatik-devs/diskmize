"""Cross-platform "open" and "reveal in file manager" helpers.

The prototype called ``os.startfile`` unconditionally, which only exists on
Windows and crashed on Linux and macOS.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

TIMEOUT_SECONDS = 20


def _run(command: list[str]) -> tuple[bool, str]:
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=TIMEOUT_SECONDS, check=False
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"{exc.__class__.__name__}: {exc}"
    if completed.returncode != 0:
        message = (completed.stderr or completed.stdout or "").strip()
        return False, message or f"exit code {completed.returncode}"
    return True, ""


def open_path(path: str | os.PathLike[str]) -> tuple[bool, str]:
    """Open a file with the default application."""
    target = os.fspath(path)
    if not Path(target).exists():
        return False, "path does not exist"
    if sys.platform.startswith("win"):
        try:
            os.startfile(target)  # type: ignore[attr-defined]  # noqa: S606
        except OSError as exc:
            return False, f"{exc.__class__.__name__}: {exc}"
        return True, ""
    if sys.platform == "darwin":
        return _run(["open", target])
    return _run(["xdg-open", target])


def reveal_path(path: str | os.PathLike[str]) -> tuple[bool, str]:
    """Show the parent folder of *path* in the file manager."""
    target = Path(os.fspath(path))
    if sys.platform.startswith("win"):
        try:
            os.startfile(str(target.parent))  # type: ignore[attr-defined]  # noqa: S606
        except OSError as exc:
            return False, f"{exc.__class__.__name__}: {exc}"
        return True, ""
    if sys.platform == "darwin":
        return _run(["open", "-R", str(target)])
    if not target.parent.exists():
        return False, "parent folder does not exist"
    return _run(["xdg-open", str(target.parent)])

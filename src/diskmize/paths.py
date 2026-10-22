"""Resource resolution that works from source, from a wheel and from PyInstaller."""

from __future__ import annotations

import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
_SOURCE_ROOT = PACKAGE_DIR.parent.parent


def base_dir() -> Path:
    """Directory that contains the bundled ``assets`` folder."""
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            return Path(meipass)
        return Path(sys.executable).resolve().parent
    return _SOURCE_ROOT


BASE_DIR = base_dir()


def asset_path(*parts: str) -> Path:
    """Resolve a path inside ``assets/`` without depending on the CWD."""
    relative = Path(*parts)
    for root in (BASE_DIR, PACKAGE_DIR / "assets", _SOURCE_ROOT):
        candidate = root / "assets" / relative
        if candidate.exists():
            return candidate
    return BASE_DIR / "assets" / relative


def icon_png() -> Path:
    return asset_path("icons", "logo.png")


def icon_ico() -> Path:
    return asset_path("icons", "logo.ico")

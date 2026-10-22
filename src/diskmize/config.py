"""User settings stored outside the install directory.

The prototype read ``config.txt`` from the current working directory, so the
language was ignored unless you launched the app from its own folder.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from .i18n import DEFAULT_LANGUAGE, normalize_language

SETTINGS_FILENAME = "settings.json"


def config_dir() -> Path:
    """Per-user configuration directory, honouring standard env overrides."""
    override = os.environ.get("DISKMIZE_CONFIG_DIR")
    if override:
        return Path(override).expanduser()
    if os.name == "nt":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
        return Path(base) / "DiskMize"
    if os.sys.platform == "darwin":
        return Path(os.path.expanduser("~/Library/Application Support/DiskMize"))
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return Path(base) / "diskmize"


def settings_path() -> Path:
    return config_dir() / SETTINGS_FILENAME


@dataclass
class Settings:
    language: str = DEFAULT_LANGUAGE
    theme: str = "clam"
    max_rows: int = 100

    def __post_init__(self) -> None:
        self.language = normalize_language(self.language)
        if self.max_rows <= 0:
            self.max_rows = 100


def load_settings(path: str | os.PathLike[str] | None = None) -> Settings:
    target = Path(path) if path is not None else settings_path()
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return Settings()
    if not isinstance(raw, dict):
        return Settings()
    known = {field: raw[field] for field in Settings().__dataclass_fields__ if field in raw}
    try:
        return Settings(**known)
    except TypeError:
        return Settings()


def save_settings(settings: Settings, path: str | os.PathLike[str] | None = None) -> Path:
    target = Path(path) if path is not None else settings_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(asdict(settings), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return target

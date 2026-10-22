"""Human readable formatting helpers.

Kept free of Tkinter imports so it can be unit tested headlessly.
"""

from __future__ import annotations

_UNITS = ("B", "KB", "MB", "GB", "TB", "PB")

# Backwards compatible aliases for the names used by the 0.1 prototype.
UNITS = _UNITS


def format_size(num_bytes: int | float) -> str:
    """Return a human readable size such as ``1.50 MB``.

    The prototype divided until the value fell under 1024 and then formatted
    the *original* number with the last unit, which printed absurd values for
    anything larger than a gigabyte. This implementation keeps scaling until
    the value fits the unit, including TB and PB.
    """
    if isinstance(num_bytes, bool) or not isinstance(num_bytes, (int, float)):
        raise TypeError("num_bytes must be an int or float")
    if num_bytes < 0:
        raise ValueError("num_bytes must not be negative")

    size = float(num_bytes)
    for unit in _UNITS:
        if size < 1024 or unit == _UNITS[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} {_UNITS[-1]}"


def format_timestamp(timestamp: float | None) -> str:
    """Format a POSIX timestamp for the "last modified" column."""
    if timestamp is None:
        return ""
    if timestamp <= 0:
        return ""
    return f"{datetime_from_timestamp(timestamp):%Y-%m-%d %H:%M}"


def datetime_from_timestamp(timestamp: float):
    from datetime import datetime

    return datetime.fromtimestamp(timestamp)


# Aliases kept so documentation and older snippets stay understandable.
formatear_tamanio = format_size

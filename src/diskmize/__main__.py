"""``python -m diskmize`` entry point."""

from __future__ import annotations

from .app import create_app


def main() -> int:
    app = create_app()
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

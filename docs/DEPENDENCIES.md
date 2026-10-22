# DiskMize Dependencies

This document describes the dependency declarations and verification commands for DiskMize.

## Source of truth

`pyproject.toml` is the canonical source for project metadata and dependency declarations. Keep `requirements.txt` and `requirements-dev.txt` consistent with it when they are changed.

## Runtime dependencies

| Package | Declared requirement | Purpose |
|---|---|---|
| Pillow | `Pillow>=10.0,<11.0` | Image and icon resource support |
| ttkthemes | `ttkthemes>=3.0.0` | Tk themed widgets |

The exact usage of each dependency should be verified against the current source before changing or removing it.

## Development dependencies

| Package | Declared requirement | Purpose |
|---|---|---|
| pytest | `pytest>=8.0` | Test runner |
| pytest-cov | `pytest-cov>=5.0` | Test coverage reporting |
| Ruff | `ruff>=0.6` | Linting and formatting checks |
| mypy | `mypy>=1.0` | Static type checking |

## System requirements

- Python `>=3.12`
- Tkinter and the system's Tcl/Tk components

Tkinter is distributed with Python, but some Linux distributions package its Tcl/Tk bindings separately. Install the appropriate system package if `import tkinter` fails.

## Set up a development environment

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Verification

Run the following checks:

```bash
python -m pip check
python -m pytest -q
python -m ruff check src tests
python -m ruff format --check src tests
```

Run `mypy` only with the project's intended configuration and target paths; do not assume that an unconfigured whole-project invocation is an established passing check.

GUI integration tests may require an active desktop session or Xvfb.

## Third-party licenses

Review the licenses for the exact dependency versions and bundled resources distributed with DiskMize. `THIRD_PARTY_NOTICES` and `THIRD_PARTY_LICENSES/` should cover components and resources actually included in the distribution. Development tools that are not shipped with the application should not be described as bundled runtime components.

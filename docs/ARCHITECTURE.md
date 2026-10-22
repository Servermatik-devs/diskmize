# DiskMize Architecture

**Project:** DiskMize  
**Version:** `0.1.0`  
**Source package:** `src/diskmize/`

This document describes the current source layout. When documentation and implementation differ, the source code is authoritative.

## Application modules

| Module | Responsibility |
|---|---|
| `app.py` | Main Tkinter application and user-interface coordination |
| `scanner.py` | File-system scanning |
| `dialogs.py` | Secondary dialogs, including About and Help |
| `deletion.py` | File-deletion operations |
| `sysopen.py` | Opening files and file-system locations |
| `paths.py` | Resolving application resource paths |
| `config.py` | Application configuration |
| `i18n.py` | English and Spanish interface translations |
| `formatting.py` | Formatting sizes and displayed values |
| `__main__.py` | Module entry point for `python -m diskmize` |

## User interface and concurrency

The main UI is implemented with Tkinter. Review `app.py` and `scanner.py` for the current scanning, cancellation, worker-thread, and UI-update behavior.

Tkinter widgets must be updated in accordance with Tkinter's threading constraints. Do not assume that arbitrary worker-thread UI updates are safe; consult the implementation before changing concurrency behavior.

## Resources and configuration

`paths.py` and `config.py` define the resource-path and configuration behavior. Source-tree execution and packaged execution can have different resource locations, so changes to assets or packaging should be checked in both contexts.

## File-system operations

`scanner.py`, `deletion.py`, and `sysopen.py` define the application's file-system behavior. Review these modules before changing scan traversal, symbolic-link handling, deletion rules, or platform-specific operations. Deletion can permanently remove data and must be treated as a destructive operation.

## Tests

Tests are located in `tests/`. Run the test suite from the project root:

```bash
python -m pytest -q
```

The test suite includes unit tests and GUI integration tests. GUI integration tests may require a graphical session or a virtual display such as Xvfb.

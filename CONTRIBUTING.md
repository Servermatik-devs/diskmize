# Contributing to DiskMize

Bug reports, documentation improvements, feature proposals and code
contributions are welcome.

## Before opening a pull request

1. Review or open an issue describing the proposed change.
2. Keep changes focused and avoid unrelated modifications.
3. Add or update tests when behavior changes.
4. Run the project checks:

   ```bash
   pytest
   ruff check .
   ruff format --check .
   python -m compileall -q src
   ```

5. Describe what changed and how it was tested.

## Pull requests

Use a descriptive title, link related issues, and do not include secrets,
personal data or unrelated generated files.

## License

DiskMize is distributed under the GNU General Public License, version 3 or,
at your option, any later version (GPL-3.0-or-later).

By submitting a contribution, you agree that it may be distributed under
that license. Only submit work you have the right to contribute.

#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -x .venv/bin/python ]]; then
    echo "ERROR: no existe .venv/bin/python" >&2
    exit 1
fi

.venv/bin/python -m pip check
.venv/bin/python -m PyInstaller \
    --noconfirm \
    --clean \
    --distpath "$ROOT/dist" \
    --workpath "$ROOT/build/pyinstaller" \
    "$ROOT/scripts/diskmize.spec"

OUT="$ROOT/dist/DiskMize"
mkdir -p "$OUT"

cp LICENSE THIRD_PARTY_NOTICES "$OUT/"
rm -rf "$OUT/THIRD_PARTY_LICENSES"
cp -a THIRD_PARTY_LICENSES "$OUT/"

echo
echo "Compilación completada: $OUT"
echo "Ejecutable: $OUT/diskmize"
echo "Licencias: $OUT/THIRD_PARTY_LICENSES"

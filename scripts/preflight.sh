#!/bin/bash
# DiskMize v0.1.0 — Preflight Checklist (CORRECTED)
set -euo pipefail

cd "$(dirname "$0")/.."

echo "╔══════════════════════════════════════════════════════╗"
echo "║       DiskMize v0.1.0 — Preflight Checklist         ║"
echo "╚══════════════════════════════════════════════════════╝"
echo

PASS=0; FAIL=0; SKIP=0; BLOCKED=0

check_pass() { echo "[PASS] $1"; ((PASS++)) || true; }
check_fail() { echo "[FAIL] $1"; ((FAIL++)) || true; }
check_skip() { echo "[SKIP] $1"; ((SKIP++)) || true; }
check_blocked() { echo "[BLOCKED] $1"; ((BLOCKED++)) || true; }

echo "┌─── SOURCE FILES ───────────────────────────────"
[[ -f "src/diskmize/__init__.py" ]] && check_pass "Main app module exists" || check_fail "Main app module missing"
[[ -f "src/diskmize/app.py" ]] && check_pass "App controller exists" || check_fail "App controller missing"
[[ -f "src/diskmize/dialogs.py" ]] && check_pass "Dialogs module exists" || check_fail "Dialogs module missing"
[[ -d "assets/icons" ]] && check_pass "Icon assets exist" || check_fail "Icon assets missing"

echo "┌─── DOCUMENTATION ───────────────────────────────"
[[ -f "README.md" ]] && check_pass "README exists" || check_fail "README missing"
[[ -f "docs/KNOWN_ISSUES.md" ]] && check_pass "Project audit exists" || check_fail "Project audit missing"
[[ -f "docs/ARCHITECTURE.md" ]] && check_pass "Architecture docs exist" || check_fail "Architecture docs missing"
[[ -f "docs/DEPENDENCIES.md" ]] && check_pass "Dependencies docs exist" || check_fail "Dependencies docs missing"

echo "┌─── BUILD & PACKAGING ────────────────────────────"
[[ -f "pyproject.toml" ]] && check_pass "pyproject.toml exists" || check_fail "pyproject.toml missing"
[[ -f "requirements.txt" ]] && check_pass "Production requirements exist" || check_fail "Production requirements missing"
[[ -f "requirements-dev.txt" ]] && check_pass "Dev requirements exist" || check_fail "Dev requirements missing"

echo "┌─── TESTING & CI ────────────────────────────────"
[[ -d "tests/unit" ]] && check_pass "Unit tests directory exists" || check_skip "Unit tests pending"
[[ -d "tests/integration" ]] && check_pass "Integration tests exist" || check_fail "Integration tests missing"

echo "┌─── LEGAL & LICENSING ────────────────────────────"
[[ -f "LICENSE" ]] && check_pass "LICENSE file exists" || check_fail "LICENSE missing — choose: GPL-3.0 or MIT (see docs/DEPENDENCIES.md)"

echo "┌─── VERSION CONSISTENCY ──────────────────────────"
if python - <<'PYVERSION'
import ast
import tomllib
from pathlib import Path

with Path("pyproject.toml").open("rb") as f:
    project_version = tomllib.load(f)["project"]["version"]

tree = ast.parse(Path("src/diskmize/__init__.py").read_text(encoding="utf-8"))
module_version = None

for node in tree.body:
    if isinstance(node, ast.Assign) and any(
        isinstance(target, ast.Name) and target.id == "__version__"
        for target in node.targets
    ):
        module_version = ast.literal_eval(node.value)
        break
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "__version__":
        module_version = ast.literal_eval(node.value)
        break

if module_version is None:
    raise SystemExit("Missing __version__ in src/diskmize/__init__.py")
if project_version != module_version:
    raise SystemExit(f"Version mismatch: pyproject={project_version}, module={module_version}")

print(f"Versions match: {project_version}")
PYVERSION
then
    check_pass "Package and module versions match"
else
    check_fail "Package and module versions differ"
fi

echo "┌─── PYTHON SYNTAX ────────────────────────────────"
if python -m compileall -q src/ tests/ 2>/dev/null; then
  check_pass "Python syntax valid for all modules"
else
  check_fail "Python syntax errors found — run: ruff check src/"
fi

echo
echo "┌─── SUMMARY ──────────────────────────────────────"
echo "  PASS: $PASS   FAIL: $FAIL   SKIP: $SKIP   BLOCKED: $BLOCKED"
echo "└──────────────────────────────────────────────────"

if [[ $FAIL -gt 0 ]] || [[ $BLOCKED -gt 0 ]]; then
  echo
  echo "[BLOCKED] Please resolve issues before proceeding"
  exit 1
elif [[ $SKIP -eq 0 ]] && [[ $BLOCKED -eq 0 ]]; then
  echo
  echo "[PASS] All checks passed — safe to proceed with next step"
  exit 0
else
  echo
  echo "[INFO] Partial success — review SKIP and BLOCKED items above"
  exit 0
fi

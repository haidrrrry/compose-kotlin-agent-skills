#!/usr/bin/env bash
# Regenerate api/skills.lock after any SKILL.md edit. Commit the lock file in the same PR.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/scripts/validate_skills.py" --write-lock "$ROOT/api/skills.lock"
python3 "$ROOT/scripts/validate_skills.py" --strict --lock-check "$ROOT/api/skills.lock"
echo "OK — api/skills.lock updated. Commit it with your SKILL.md changes."

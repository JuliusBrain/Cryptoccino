#!/usr/bin/env bash
# PostToolUse check. After Claude edits a pipeline/ module, run the matching
# unit test (falling back to the full unit suite) so resilience/curation
# regressions surface immediately, per the goal-driven rule in CLAUDE.md.
#
# Non-blocking: a failure is reported back to Claude as context (exit 2) but
# only for edits under pipeline/. Edits elsewhere are ignored (exit 0).

set -uo pipefail

payload="$(cat)"
path="$(printf '%s' "$payload" | jq -r '.tool_input.file_path // empty')"
[ -z "$path" ] && exit 0

root="${CLAUDE_PROJECT_DIR:-$PWD}"
rel="${path#"$root/"}"

# Only react to edits of pipeline source.
case "$rel" in
  pipeline/*.py) ;;
  *) exit 0 ;;
esac

py="$root/.venv/bin/python"
[ -x "$py" ] || py="$(command -v python3)"
[ -n "$py" ] || { echo "test-on-edit: no python interpreter found; skipping." >&2; exit 0; }

# Map pipeline/foo.py -> tests/unit/test_foo.py when it exists.
module="$(basename "$rel" .py)"
target="tests/unit/test_${module}.py"
[ -f "$root/$target" ] || target="tests/unit"

cd "$root"
if ! out="$("$py" -m pytest "$target" -q 2>&1)"; then
  echo "Tests failed after editing $rel:" >&2
  echo "$out" | tail -30 >&2
  exit 2
fi

exit 0

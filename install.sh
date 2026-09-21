#!/usr/bin/env bash
# Local-only wrapper; it neither downloads dependencies nor changes host settings.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
  exec python3 "$SCRIPT_DIR/install.py" "$@"
elif command -v python >/dev/null 2>&1; then
  exec python "$SCRIPT_DIR/install.py" "$@"
else
  printf '%s\n' "Python 3.9+ was not found. Use the manual folder-copy method in README.md." >&2
  exit 1
fi

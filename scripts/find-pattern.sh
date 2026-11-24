#!/usr/bin/env bash
# Usage: find-pattern.sh <query>
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
QUERY="${1:-}"
if [[ -z "$QUERY" ]]; then
  echo "Usage: find-pattern.sh <regex or name>" >&2
  exit 1
fi
rg -i --heading --line-number "$QUERY" "$ROOT/library" || true
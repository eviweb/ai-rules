#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV="${REPO_ROOT}/.venv"

if [[ ! -f "${VENV}/bin/python3" ]]; then
  echo "Virtual environment not found. Run: uv pip install -e '.[dev]'" >&2
  exit 1
fi

exec "${VENV}/bin/python3" -m pytest "$@"

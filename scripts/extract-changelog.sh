#!/usr/bin/env bash
set -euo pipefail

# extract-changelog.sh — Extract release notes for a given version from CHANGELOG.md

SCRIPT_NAME="$(basename "$0")"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_VERSION="$(cat "${SCRIPT_DIR}/../VERSION" 2>/dev/null || echo "unknown")"

CHANGELOG="${PWD}/CHANGELOG.md"

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

cleanup() { :; }
trap cleanup EXIT INT TERM

# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------

usage() {
  cat <<EOF
Usage: ${SCRIPT_NAME} [options] <version>

Extract release notes for a given version from CHANGELOG.md.
Output is written to stdout and can be piped directly to release tools.

Arguments:
  <version>                Version to extract (e.g. 1.2.3 or 1.0.0-rc.1)

Options:
  -c|--changelog <path>    Path to CHANGELOG.md (default: ./CHANGELOG.md)
  -h|--help                Display this help message and exit
  -V|--version             Display script version and exit
  --debug                  Enable trace mode (set -x)

Examples:
  ${SCRIPT_NAME} 1.2.3
  ${SCRIPT_NAME} --changelog /path/to/CHANGELOG.md 1.2.3
  gh release create 1.2.3 --notes-file <(${SCRIPT_NAME} 1.2.3)
EOF
}

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

TARGET_VERSION=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    -V|--version)
      echo "${SCRIPT_NAME} ${SCRIPT_VERSION}"
      exit 0
      ;;
    --debug)
      set -x
      ;;
    -c|--changelog)
      [[ -z "${2:-}" ]] && { echo "Error: --changelog requires a path" >&2; exit 1; }
      CHANGELOG="$2"
      shift
      ;;
    -*)
      echo "Error: unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
    *)
      if [[ -n "$TARGET_VERSION" ]]; then
        echo "Error: unexpected argument: $1" >&2
        usage >&2
        exit 1
      fi
      TARGET_VERSION="$1"
      ;;
  esac
  shift
done

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

if [[ -z "$TARGET_VERSION" ]]; then
  echo "Error: version argument is required" >&2
  usage >&2
  exit 1
fi

if [[ ! -f "$CHANGELOG" ]]; then
  echo "Error: changelog not found: ${CHANGELOG}" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

# Use index() for literal string matching — avoids regex escaping issues
# with semver strings containing dots or pre-release metadata (e.g. 1.0.0-rc.1)
result="$(awk -v version="[${TARGET_VERSION}]" '
  /^## \[/ {
    if (found) exit
    if (index($0, version) > 0) { found=1; next }
  }
  found { print }
' "$CHANGELOG")"

if [[ -z "$result" ]]; then
  echo "Error: version [${TARGET_VERSION}] not found in ${CHANGELOG}" >&2
  exit 1
fi

# Strip leading and trailing blank lines
echo "$result" | sed -e '/./,$!d' -e 's/[[:space:]]*$//'

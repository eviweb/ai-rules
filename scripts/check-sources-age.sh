#!/usr/bin/env bash
# check-sources-age.sh — list the rows of docs/sources.md that are due for a review.
#
# Internal read-only helper: it supports -h, -V and --debug only, plus the
# options below. Exit codes: 0 nothing due, 1 something is due, 2 usage or input error.

set -euo pipefail

SCRIPT_NAME="check-sources-age.sh"
SCRIPT_VERSION="1.0.0"
UPSTREAM_REPO="obra/superpowers"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FILE="${ROOT}/docs/sources.md"
TODAY="$(date +%Y-%m-%d)"
CHECK_UPSTREAM=0
LATEST_UPSTREAM=""

usage() {
  cat <<USAGE
Usage: ${SCRIPT_NAME} [options]

List the rows of the sources register that are due for a review: a verified
date older than its review period, or never verified. With --check-upstream,
also compare the pinned Superpowers commit with the latest upstream commit.

Options:
  --file <path>              Register to read (default: docs/sources.md)
  --today <YYYY-MM-DD>       Date used as today (default: the system date)
  --check-upstream           Compare the pinned upstream commit with the latest one
  --latest-upstream <sha>    Use this value instead of querying GitHub (offline, tests)
  -h, --help                 Show this help and exit
  -V, --version              Show the version and exit
  --debug                    Trace the execution (set -x)

Exit status: 0 nothing due, 1 something is due, 2 usage or input error.
USAGE
}

die() {
  echo "Error: $*" >&2
  exit 2
}

is_date() {
  [[ "$1" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] && date -d "$1" +%F >/dev/null 2>&1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)
      [[ $# -ge 2 ]] || die "--file requires a path"
      FILE="$2"
      shift 2
      ;;
    --today)
      [[ $# -ge 2 ]] || die "--today requires a date"
      is_date "$2" || die "--today must be a valid YYYY-MM-DD date, got '$2'"
      TODAY="$2"
      shift 2
      ;;
    --check-upstream) CHECK_UPSTREAM=1; shift ;;
    --latest-upstream)
      [[ $# -ge 2 ]] || die "--latest-upstream requires a commit"
      LATEST_UPSTREAM="$2"
      shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    -V|--version) echo "${SCRIPT_NAME} ${SCRIPT_VERSION}"; exit 0 ;;
    --debug) set -x; shift ;;
    *) die "unknown option: $1 (see --help)" ;;
  esac
done

[[ -f "$FILE" ]] || die "register not found: ${FILE}"

due=()
upstream_pin=""

while IFS='|' read -r _ source version reference verified every status _; do
  source="$(echo "$source" | xargs)"
  verified="$(echo "$verified" | xargs)"
  every="$(echo "$every" | xargs)"
  version="$(echo "$version" | xargs)"
  reference="$(echo "$reference" | xargs)"
  status="$(echo "$status" | xargs)"

  # Only data rows: the verified column holds a date or "never".
  if [[ "$verified" != "never" ]] && ! is_date "$verified"; then
    continue
  fi
  [[ "$every" =~ ^[0-9]+$ ]] || die "row '${source}': review period must be a number of months, got '${every}'"

  if [[ "$source" == Superpowers* && "$version" =~ @[[:space:]]*([0-9a-f]{7,40}) ]]; then
    upstream_pin="${BASH_REMATCH[1]}"
  fi

  if [[ "$verified" == "never" ]]; then
    due+=("- **${source}**: never verified (${status}). Check ${reference}")
    continue
  fi
  due_date="$(date -d "${verified} + ${every} months" +%F)"
  if [[ "$TODAY" > "$due_date" || "$TODAY" == "$due_date" ]]; then
    due+=("- **${source}**: last verified ${verified}, review was due ${due_date} (${status}). Check ${reference}")
  fi
done < <(grep '^|' "$FILE")

if [[ "$CHECK_UPSTREAM" -eq 1 ]]; then
  [[ -n "$upstream_pin" ]] || die "no pinned Superpowers commit found in ${FILE}"
  latest="$LATEST_UPSTREAM"
  if [[ -z "$latest" ]]; then
    command -v curl >/dev/null 2>&1 || die "curl is required for --check-upstream"
    latest="$(curl -fsS "https://api.github.com/repos/${UPSTREAM_REPO}/commits?per_page=1" \
      | grep -m1 '"sha"' | sed -E 's/.*"sha": *"([0-9a-f]+)".*/\1/')" \
      || die "could not read the latest commit of ${UPSTREAM_REPO}"
  fi
  [[ -n "$latest" ]] || die "no upstream commit found"
  if [[ "${latest:0:${#upstream_pin}}" != "$upstream_pin" ]]; then
    due+=("- **Superpowers**: upstream moved from ${upstream_pin} to ${latest:0:7}. Review the diff of the derived skills (see THIRD_PARTY.md)")
  fi
fi

if [[ ${#due[@]} -eq 0 ]]; then
  echo "All sources are up to date (${TODAY})."
  exit 0
fi

echo "# Sources review due (${TODAY})"
echo
printf '%s\n' "${due[@]}"
echo
echo "Update docs/sources.md (version, date, status) after each check."
exit 1

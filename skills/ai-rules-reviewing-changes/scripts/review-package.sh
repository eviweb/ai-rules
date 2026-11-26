#!/usr/bin/env bash
# review-package.sh — write one file with everything a review of the current
# change needs: commits since the base, then the staged, unstaged and untracked
# files against the base, as a stat summary and a diff with extended context.
#
# Internal read-only helper: it never changes the index, the working tree or
# the branch. It supports -h, -V and --debug, plus the options below.
# Exit codes: 0 package written, 2 usage or input error, 3 nothing to review.

set -euo pipefail

SCRIPT_NAME="review-package.sh"
SCRIPT_VERSION="1.0.0"
CONTEXT_LINES=10
BASE=""
OUTPUT=""

usage() {
  cat <<USAGE
Usage: ${SCRIPT_NAME} [options]

Write a review package of the current change: the commits since the base, then
every staged, unstaged and untracked (not ignored) file compared with the base.
Prints the path of the package, the number of files and its size.

Options:
  --base <ref>         Compare with this commit (default: merge base with main,
                       or master when main does not exist)
  -o, --output <path>  Write the package here (default:
                       .private/reviews/review-<base>-<timestamp>.md)
  -h, --help           Show this help and exit
  -V, --version        Show the version and exit
  --debug              Trace the execution (set -x)

Exit status: 0 package written, 2 usage or input error, 3 nothing to review.
USAGE
}

die() {
  echo "Error: $*" >&2
  exit 2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base)
      [[ $# -ge 2 ]] || die "--base requires a commit"
      BASE="$2"
      shift 2
      ;;
    -o | --output)
      [[ $# -ge 2 ]] || die "--output requires a path"
      OUTPUT="$2"
      shift 2
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    -V | --version)
      echo "${SCRIPT_NAME} ${SCRIPT_VERSION}"
      exit 0
      ;;
    --debug)
      set -x
      shift
      ;;
    *)
      usage >&2
      die "unknown option: $1"
      ;;
  esac
done

command -v git >/dev/null 2>&1 || die "git is required"

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || die "not a git repository: $(pwd)"
cd "${ROOT}"

default_base() {
  local branch
  for branch in main master; do
    if git rev-parse --verify --quiet "refs/heads/${branch}" >/dev/null; then
      git merge-base "${branch}" HEAD
      return
    fi
  done
  die "no main or master branch: pass --base"
}

if [[ -z "${BASE}" ]]; then
  BASE="$(default_base)"
fi
BASE_SHA="$(git rev-parse --verify --quiet "${BASE}^{commit}")" || die "unknown base: ${BASE}"
BASE_SHORT="$(git rev-parse --short=7 "${BASE_SHA}")"

# Untracked files that are not ignored, except earlier review packages.
mapfile -t UNTRACKED < <(git ls-files --others --exclude-standard -- . ':(exclude).private/reviews')

if git diff --quiet "${BASE_SHA}" -- && [[ ${#UNTRACKED[@]} -eq 0 ]]; then
  echo "Error: nothing to review: no change since ${BASE_SHORT}" >&2
  exit 3
fi

if [[ -z "${OUTPUT}" ]]; then
  OUTPUT="${ROOT}/.private/reviews/review-${BASE_SHORT}-$(date +%Y%m%d-%H%M%S).md"
fi
mkdir -p "$(dirname "${OUTPUT}")"

# Write to a temporary file and move it into place at the end, so that an
# error or an interruption never leaves a partial package behind.
PARTIAL="$(mktemp "${OUTPUT}.partial.XXXXXX")"
cleanup() { rm -f "${PARTIAL}"; }
trap cleanup EXIT INT TERM

untracked_diff() {
  local file status
  for file in "${UNTRACKED[@]}"; do
    # git diff --no-index exits 1 when the files differ, which is always the
    # case against /dev/null; only a status above 1 is an error.
    status=0
    git diff --no-index -U"${CONTEXT_LINES}" -- /dev/null "${file}" || status=$?
    [[ ${status} -le 1 ]] || die "cannot diff untracked file: ${file}"
  done
}

{
  echo "# Review package"
  echo
  echo "- Base: ${BASE_SHORT} ($(git log -1 --format=%s "${BASE_SHA}"))"
  echo "- Branch: $(git rev-parse --abbrev-ref HEAD)"
  echo "- Written: $(date '+%Y-%m-%d %H:%M:%S')"
  echo
  echo "## Commits since the base"
  echo
  COMMITS="$(git log --format='- %h %s' "${BASE_SHA}..HEAD")"
  echo "${COMMITS:-(none)}"
  echo
  echo "## Files changed (commits, index and working tree)"
  echo
  echo '```'
  git diff --stat "${BASE_SHA}" --
  echo '```'
  if [[ ${#UNTRACKED[@]} -gt 0 ]]; then
    echo
    echo "## Untracked files (new, not yet added)"
    echo
    printf -- '- %s\n' "${UNTRACKED[@]}"
  fi
  echo
  echo "## Diff"
  echo
  # Five backticks: the diff often holds Markdown code blocks of three.
  echo '`````diff'
  git diff -U"${CONTEXT_LINES}" "${BASE_SHA}" --
  untracked_diff
  echo '`````'
} >"${PARTIAL}"
mv "${PARTIAL}" "${OUTPUT}"

FILES="$(( $(git diff --name-only "${BASE_SHA}" -- | wc -l) + ${#UNTRACKED[@]} ))"
echo "wrote ${OUTPUT}: ${FILES} file(s), $(wc -c <"${OUTPUT}" | tr -d ' ') bytes"

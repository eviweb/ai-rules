#!/usr/bin/env bash
set -euo pipefail

# measure-context.sh — Measure the size of each rule-loading layer as a Markdown table

SCRIPT_NAME="$(basename "$0")"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_VERSION="$(cat "${SCRIPT_DIR}/../VERSION" 2>/dev/null || echo "unknown")"

ROOT="${SCRIPT_DIR}/.."
SHOW_FILES=0

usage() {
  cat <<EOF
Usage: ${SCRIPT_NAME} [options]

Print byte, line and approximate token counts (bytes / 4, rounded up) for each
layer that loads rules into an agent session. Output is a Markdown table.
Token counts are an estimate: confirm with /context in a real session.

Options:
  -r|--root <path>   Repository root (default: parent of this script)
  --files            Also list every file of the rules/ directory
  -h|--help          Display this help message and exit
  -V|--version       Display script version and exit
  --debug            Enable trace mode (set -x)

Exit codes: 0 success, 2 misuse (bad arguments or missing root)
EOF
}

die() {
  echo "Error: $1" >&2
  exit 2
}

# Print "<files> <bytes> <lines>" for the files passed as arguments.
count_files() {
  local files=0 bytes=0 lines=0 file
  for file in "$@"; do
    [[ -f "$file" ]] || continue
    files=$((files + 1))
    bytes=$((bytes + $(wc -c < "$file")))
    lines=$((lines + $(wc -l < "$file")))
  done
  echo "${files} ${bytes} ${lines}"
}

print_row() {
  local label="$1"
  shift
  local files bytes lines
  read -r files bytes lines <<< "$(count_files "$@")"
  printf '| %s | %s | %s | %s | %s |\n' "$label" "$files" "$bytes" "$lines" "$(((bytes + 3) / 4))"
}

# Print the rule files imported by an entry point (@rules/x.md or @./rules/x.md).
list_imports() {
  local entry_point="$1"
  [[ -f "$entry_point" ]] || return 0
  { grep -oE '^@(\./)?rules/[^[:space:]]+' "$entry_point" || true; } \
    | sed -E 's#^@(\./)?#'"${ROOT}"'/#'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -r|--root)
      [[ $# -ge 2 ]] || die "--root requires a path"
      ROOT="$2"
      shift 2
      ;;
    --files) SHOW_FILES=1; shift ;;
    -h|--help) usage; exit 0 ;;
    -V|--version) echo "${SCRIPT_NAME} ${SCRIPT_VERSION}"; exit 0 ;;
    --debug) set -x; shift ;;
    *) die "unknown option: $1 (see --help)" ;;
  esac
done

[[ -d "$ROOT" ]] || die "root directory not found: ${ROOT}"
ROOT="$(cd "$ROOT" && pwd)"

claude_entry="${ROOT}/agents/claude/CLAUDE.md"
gemini_entry="${ROOT}/agents/gemini/GEMINI.md"
mapfile -t claude_imports < <(list_imports "$claude_entry")
mapfile -t gemini_imports < <(list_imports "$gemini_entry")
mapfile -t rules_dir < <(find "${ROOT}/rules" -maxdepth 1 -name '*.md' 2>/dev/null | sort)

echo "| Layer | Files | Bytes | Lines | ~Tokens |"
echo "|-------|-------|-------|-------|---------|"
print_row "Claude Code @imports" "$claude_entry" "${claude_imports[@]}"
print_row "rules/ directory" "${rules_dir[@]}"
[[ -d "${ROOT}/core" ]] && print_row "core/" "${ROOT}"/core/*.md
[[ -d "${ROOT}/skills" ]] && print_row "skills/" "${ROOT}"/skills/*/SKILL.md
print_row "Gemini @imports" "$gemini_entry" "${gemini_imports[@]}"
print_row "Codex flat file" "${ROOT}/agents/codex/AGENTS.md"

double_loaded=()
for imported in "${claude_imports[@]}"; do
  for candidate in "${rules_dir[@]}"; do
    [[ "$imported" == "$candidate" ]] && double_loaded+=("$(basename "$imported")")
  done
done

echo
echo "Double-loaded: ${#double_loaded[@]} files (imported by CLAUDE.md and also present in rules/, which is auto-loaded when deployed to ~/.claude/rules)"

if [[ "$SHOW_FILES" -eq 1 ]]; then
  echo
  echo "| File | Files | Bytes | Lines | ~Tokens |"
  echo "|------|-------|-------|-------|---------|"
  for file in "${rules_dir[@]}"; do
    print_row "rules/$(basename "$file")" "$file"
  done
fi

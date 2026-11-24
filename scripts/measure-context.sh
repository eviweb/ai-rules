#!/usr/bin/env bash
set -euo pipefail

# measure-context.sh — Measure the size of each rule-loading layer as a Markdown table

SCRIPT_NAME="$(basename "$0")"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_VERSION="$(cat "${SCRIPT_DIR}/../VERSION" 2>/dev/null || echo "unknown")"

ROOT="${SCRIPT_DIR}/.."
SHOW_FILES=0
# Calibrated against /context (2026-11-19, 26.8k tokens for 71,680 bytes of rules); model dependent
BYTES_PER_TOKEN="2.7"

usage() {
  cat <<EOF
Usage: ${SCRIPT_NAME} [options]

Print byte, line and approximate token counts (bytes / bytes-per-token, rounded
up) for each layer that loads rules into an agent session. Output is a Markdown
table. Token counts are an estimate calibrated on one model: confirm with
/context in a real session.

Options:
  -r|--root <path>   Repository root (default: parent of this script)
  --files            Also list every file of the rules/ directory
  --bytes-per-token <n>
                     Bytes per token used for the estimate (default: ${BYTES_PER_TOKEN},
                     measured with /context; plain prose is closer to 4)
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

# Print the ceiling of <bytes> / BYTES_PER_TOKEN.
estimate_tokens() {
  awk -v bytes="$1" -v ratio="$BYTES_PER_TOKEN" 'BEGIN { t = bytes / ratio; n = int(t); if (t - n > 1e-9) n++; print n }'
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
  printf '| %s | %s | %s | %s | %s |\n' "$label" "$files" "$bytes" "$lines" "$(estimate_tokens "$bytes")"
}

# Print the value of a top-level frontmatter <key> of a SKILL.md, without quotes.
frontmatter_value() {
  local file="$1" key="$2"
  awk -v key="$key" '
    NR == 1 && $0 != "---" { exit }
    NR > 1 && $0 == "---" { exit }
    index($0, key ": ") == 1 {
      value = substr($0, length(key) + 3)
      gsub(/^["\047]|["\047]$/, "", value)
      print value
      exit
    }' "$file"
}

# Print one table row for the skill listing: name + description of every SKILL.md,
# the only skill text the agent pays at every turn.
print_listing_row() {
  local label="$1"
  shift
  local files=0 bytes=0 file name description
  for file in "$@"; do
    [[ -f "$file" ]] || continue
    name="$(frontmatter_value "$file" name)"
    description="$(frontmatter_value "$file" description)"
    files=$((files + 1))
    bytes=$((bytes + $(printf '%s%s' "$name" "$description" | wc -c)))
  done
  printf '| %s | %s | %s | - | %s |\n' "$label" "$files" "$bytes" "$(estimate_tokens "$bytes")"
}

# Print the rule files imported by an entry point (@core/x.md, @rules/x.md or the @./ form).
list_imports() {
  local entry_point="$1"
  [[ -f "$entry_point" ]] || return 0
  { grep -oE '^@(\./)?(core|rules)/[^[:space:]]+' "$entry_point" || true; } \
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
    --bytes-per-token)
      [[ $# -ge 2 ]] || die "--bytes-per-token requires a value"
      if ! [[ "$2" =~ ^[0-9]+(\.[0-9]+)?$ ]] || ! awk -v v="$2" 'BEGIN { exit !(v > 0) }'; then
        die "--bytes-per-token must be a positive number, got '$2'"
      fi
      BYTES_PER_TOKEN="$2"
      shift 2
      ;;
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
if [[ -d "${ROOT}/skills" ]]; then
  mapfile -t skill_files < <(find "${ROOT}/skills" -mindepth 2 -maxdepth 2 -name SKILL.md | sort)
  mapfile -t skill_references < <(find "${ROOT}/skills" -mindepth 3 -path '*/references/*' -name '*.md' | sort)
  print_listing_row "skills/ listing (always on)" "${skill_files[@]}"
  print_row "skills/ SKILL.md (on demand)" "${skill_files[@]}"
  [[ ${#skill_references[@]} -gt 0 ]] && print_row "skills/ references (on demand)" "${skill_references[@]}"
fi
print_row "Gemini @imports" "$gemini_entry" "${gemini_imports[@]}"
print_row "Codex flat file" "${ROOT}/agents/codex/AGENTS.md"

overlapping=()
for imported in "${claude_imports[@]}"; do
  for candidate in "${rules_dir[@]}"; do
    [[ "$imported" == "$candidate" ]] && overlapping+=("$(basename "$imported")")
  done
done

if [[ -d "${ROOT}/skills" ]]; then
  echo
  echo "Skills: only the skill listing is paid at every turn (name + description, bytes of the frontmatter values); SKILL.md and references are read when a skill is invoked."
fi

echo
echo "Overlap: ${#overlapping[@]} files are both imported by CLAUDE.md and present in rules/ (auto-loaded when deployed to ~/.claude/rules). Claude Code loads each once when both resolve to the same real path (symlink deployment); verify with /context."

if [[ "$SHOW_FILES" -eq 1 ]]; then
  echo
  echo "| File | Files | Bytes | Lines | ~Tokens |"
  echo "|------|-------|-------|-------|---------|"
  for file in "${rules_dir[@]}"; do
    print_row "rules/$(basename "$file")" "$file"
  done
fi

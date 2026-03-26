#!/usr/bin/env bash
set -euo pipefail

# install.sh — Deploy claude-config symlinks into ~/.claude/

SCRIPT_NAME="$(basename "$0")"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="${HOME}/.claude"
BACKUP_DIR="${CLAUDE_DIR}/backup-$(date +%Y%m%d-%H%M%S)"

DRY_RUN=0
VERBOSE=0

# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

_log() {
  local level="$1"
  shift
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [${level}] $*"
}

info()    { _log "INFO"  "$@"; }
warn()    { _log "WARN"  "$@" >&2; }
error()   { _log "ERROR" "$@" >&2; }
verbose() { if [[ $VERBOSE -eq 1 ]]; then _log "DEBUG" "$@"; fi; }

# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------

usage() {
  cat <<EOF
Usage: ${SCRIPT_NAME} [options]

Deploy claude-config by creating symlinks in ~/.claude/.

Options:
  -h, --help      Display this help message and exit
  -n, --dry-run   Simulate installation without making any changes
  -v, --verbose   Enable verbose output
EOF
}

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)     usage; exit 0 ;;
    -n|--dry-run)  DRY_RUN=1 ;;
    -v|--verbose)  VERBOSE=1 ;;
    *) error "Unknown option: $1"; usage >&2; exit 1 ;;
  esac
  shift
done

# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

link_target() {
  local source="$1"
  local target="$2"
  local name
  name="$(basename "$target")"

  if [[ -L "$target" ]]; then
    verbose "${name}: already a symlink — skipping"
    return
  fi

  if [[ -e "$target" ]]; then
    warn "${name}: exists and is not a symlink — backing up to ${BACKUP_DIR}/"
    if [[ $DRY_RUN -eq 0 ]]; then
      mkdir -p "$BACKUP_DIR"
      mv "$target" "$BACKUP_DIR/"
    fi
  fi

  info "${name}: ${target} -> ${source}"
  if [[ $DRY_RUN -eq 0 ]]; then
    ln -s "$source" "$target"
  fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

[[ $DRY_RUN -eq 1 ]] && info "Dry run mode — no changes will be made"

link_target "${SCRIPT_DIR}/CLAUDE.md"      "${CLAUDE_DIR}/CLAUDE.md"
link_target "${SCRIPT_DIR}/rules"          "${CLAUDE_DIR}/rules"
link_target "${SCRIPT_DIR}/settings.json"  "${CLAUDE_DIR}/settings.json"

info "Done."

# Shell (bash, zsh, POSIX sh)

## Idioms
- `set -euo pipefail`, a `main` function, `local` in functions, quote every expansion (`"$var"`, `"${arr[@]}"`).
- `[[ ]]` over `[ ]` in bash; `printf` over `echo` for data; `mapfile` or `while read -r` over parsing `ls`.
- Extract repeated pipelines into functions; move shared code to a sourced `lib/` file.
- `trap cleanup EXIT` for temporary files; subshell or `pushd/popd` instead of a bare `cd`.

## Signals
- Unquoted variables, `eval`, `|| true` without a reason, parsing `ls` or `ps` output.
- One long script with global variables and no functions; the same `sed` or `awk` hack pasted several times.
- Options parsed by hand in three different ways.

## Detectors
- `shellcheck` (always), `shfmt -d` (formatting), `bats` (tests), `kcov` (coverage), `bashate` (style).
- Refactor under test: characterization with `bats` on the current output first.

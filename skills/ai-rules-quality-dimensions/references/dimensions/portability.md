# Portability
The system works correctly across all declared target environments without environment-specific hacks.

- Follow XDG Base Directory spec for file locations (see `rules/compatibility.md`)
- Never hardcode absolute paths — use relative paths or configurable roots
- Test on all declared platforms (Ubuntu LTS, Termux) before release
- Document environment requirements and compatibility constraints in `README.md`

Red flags: hardcoded `/home/username/`, Linux-only syscalls without a fallback, dependencies that don't exist on Termux, undocumented OS assumptions.

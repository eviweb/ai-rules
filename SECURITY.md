# Security Policy

## Supported versions

Only the latest release on `main` receives security fixes.

## Reporting a vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report vulnerabilities by emailing the maintainer directly:

- **Email**: dev@eviweb.fr
- **Subject**: `[ai-rules] Security vulnerability`

Please include:
- A description of the vulnerability and its potential impact
- Steps to reproduce or a proof-of-concept
- Any suggested remediation if you have one

You will receive an acknowledgement within 48 hours and a status update
within 7 days.

## Scope

This project is a local CLI tool that manages symlinks and configuration files
on the user's own machine. It does not handle credentials, network requests,
or multi-user environments. The primary risk surface is:

- Symlink injection via a malicious `agents.toml`
- TOML config patching writing unexpected values to user config files

## Out of scope

- Vulnerabilities in third-party AI assistants (Claude Code, Codex, Gemini)
- Issues that require physical access to the user's machine

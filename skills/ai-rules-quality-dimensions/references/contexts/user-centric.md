# User-centric design

Read when the project has end users, including developers who use a CLI, a library or an API.

## Process (ISO 9241-210, human-centred design)

1. Understand the users and the context of use: who they are, what they are trying to do, where, with which constraints.
2. State the user requirements as outcomes ("a new user can install and run the first command in five minutes").
3. Produce a design, the cheaper the better: a sketch, a paper flow, a command transcript, a prototype.
4. Evaluate it against the requirements with real users or real use; five users find most of the problems.
5. Iterate. Frame the need with a *job to be done*: "when X, I want to Y, so that Z".

## Usability heuristics (Nielsen)

Visibility of system status; match with the real world; user control and freedom (undo, cancel); consistency and standards; error prevention; recognition over recall; flexibility for novices and experts; minimalist design; help users recognise, diagnose and recover from errors; help and documentation.

## Design principles (Norman)

Make actions discoverable (signifiers), give immediate and clear feedback, use constraints to prevent mistakes, keep mappings natural, and design so that the conceptual model is visible.

## In practice

- **Defaults** do the common thing; configuration is for exceptions (convention over configuration).
- **Progressive disclosure**: simple cases first, advanced options on request.
- **Prevent and recover**: confirm destructive actions, offer `--dry-run`, make undo possible, explain how to fix an error.
- **Feedback and time**: acknowledge within 0.1 s, show progress after 1 s, give a status for anything beyond 10 s.
- **Plain language** in messages and labels; no jargon the user did not choose.
- **Inclusive**: design for different abilities, devices and languages; see [accessibility](accessibility.md).
- **No dark patterns**: no hidden costs, forced continuity, confirm-shaming, or choices that nudge against the user's interest.

## CLI and API ergonomics

- Human-first output by default and a machine-readable mode (`--json`); exit codes that mean something; examples in `--help`; colour only on a terminal; progress on stderr (see `rules/cli.md`).
- Predictable names and verbs across commands; the same flag means the same thing everywhere.
- APIs: consistent naming and error shape, documented examples, versioned changes (see `rules/api.md`), a quick start that works as written.

## Red flags

Options nobody can find, errors that blame the user, a first run that needs reading a manual, behaviour that differs between commands for no reason, telemetry added without telling anyone.

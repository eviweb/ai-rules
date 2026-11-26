# Global Rules

## Always loaded (core)
@../../core/language.md
@../../core/principles.md
@../../core/security.md
@../../core/commits.md
@../../core/git.md

Topic rules in `rules/` carry a `paths:` frontmatter: Claude Code loads each one only when it reads or writes a matching file.

## Skills (on demand)
Typical flow: brainstorming (frame the problem, options) → spec → plan → test-driven development with refactoring → verification before completion → review → finish the branch.

- `ai-rules-brainstorming`: before building something new or changing behavior when the need or its why is unsettled, or when asked what to do next
- `ai-rules-writing-plans`: an approved spec or design needs several steps, before touching code
- `ai-rules-executing-plans`: the user approved a plan and asked to execute it
- `ai-rules-starting-a-project`: new project or repository (initial files, `.editorconfig`, first commit)
- `ai-rules-quality-dimensions`: designing a project or judging the quality of a significant change
- `ai-rules-reviewing-changes`: before proposing a commit or opening a PR, or when reviewing a change
- `ai-rules-pull-requests-and-issues`: writing a pull request or an issue
- `ai-rules-verification-before-completion`: about to say work is done or passing, before a commit message or a PR
- `ai-rules-systematic-debugging`: a bug, failing test, CI failure or unexpected behavior, before proposing a fix
- `ai-rules-test-driven-development`: implementing a feature, fix or behavior change, before the production code
- `ai-rules-refactoring-and-design`: the Refactor step, code smells, hard-to-change code, choosing a design or pattern
- `ai-rules-architecture-proposal`: starting a project or adding a significant component, before choosing a structure
- `ai-rules-writing-documents`: writing or rewriting a README, guide, spec, design document, changelog entry or diagram

# Global Rules

## Always loaded (core)
@../../core/language.md
@../../core/principles.md
@../../core/security.md
@../../core/commits.md
@../../core/git.md

Topic rules in `rules/` carry a `paths:` frontmatter: Claude Code loads each one only when it reads or writes a matching file.

## Skills (on demand)
- `ai-rules-starting-a-project`: new project or repository (initial files, `.editorconfig`, first commit)
- `ai-rules-quality-dimensions`: designing a project or judging the quality of a significant change
- `ai-rules-reviewing-changes`: before proposing a commit or opening a PR, or when reviewing a change
- `ai-rules-pull-requests-and-issues`: writing a pull request or an issue
- `ai-rules-verification-before-completion`: about to say work is done or passing, before a commit message or a PR
- `ai-rules-systematic-debugging`: a bug, failing test, CI failure or unexpected behavior, before proposing a fix
- `ai-rules-test-driven-development`: implementing a feature, fix or behavior change, before the production code

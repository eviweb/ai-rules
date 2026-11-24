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

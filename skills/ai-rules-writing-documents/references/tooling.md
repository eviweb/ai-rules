# Documentation tooling

Use the tools the project already has. Propose a new tool only when a problem recurs (broken links found by users, inconsistent style across contributors), and ask before adding it; each tool is a dependency to maintain.

| Problem | Tool | Notes |
|---|---|---|
| Inconsistent Markdown (headings, lists, line length) | **markdownlint** (`markdownlint-cli2`) | Config in `.markdownlint.jsonc`; disable rules that fight the project's style rather than reformatting everything |
| Style and vocabulary (banned words, one term per concept, jargon) | **Vale** | Project vocabulary in `.vale/`; start with a few rules, the full packages are noisy |
| Broken links | **lychee** | Run offline (`--offline`) on each change and online on a schedule, since external sites change |
| Spelling | **codespell** | Low false positives on code; an ignore list for project terms |
| Code samples that no longer run | Executed examples | Doctests (`python -m doctest`, `pytest --doctest-glob`), a test that runs the README commands, or tools that execute fenced blocks |
| Mermaid diagrams that fail to render | **Mermaid CLI** (`mmdc`) | Render each diagram in CI or before commit; a failed render is an error |
| Reference drifting from the code | Generated reference | From `--help`, docstrings or schemas; committed or built by the docs site |

## Where to run them

- Locally through the project's pre-commit hook when it has one, for fast feedback.
- In CI on pull requests that touch documentation (`rules/ci.md`); the online link check on a schedule so that a third-party outage does not block a merge.
- Report each finding with the file and line; fix it or justify the exception in the tool's config, never silence a whole rule for one case.

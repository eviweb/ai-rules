# Writing quality

## Principles

- **Point first.** The first sentence of a document, a section or a paragraph says the most important thing: the answer, the decision, the action. Context and details follow.
- **Plain words.** Short sentences, active voice, concrete verbs. Prefer "use" to "leverage", "run" to "execute the invocation of". Explain an acronym at its first use.
- **One term per concept.** Choose a word and keep it everywhere ("project profile", not also "repo mode" and "strictness level"). Define the project's terms once, in a glossary if there are many.
- **Structure that scans.** Headings that state the content ("Install on Linux", not "Miscellaneous"), one idea per paragraph, lists for parallel items, tables to compare, numbered steps for procedures.
- **Concrete examples.** Show a real command with its real output, a real file excerpt, a real value. One good example beats a paragraph of description.
- **Reader's vocabulary.** Write in terms of what the reader wants to do, not of how the code is organized.
- **Honest scope.** State the limits, the prerequisites and what is not covered.

## Anti-patterns

| Anti-pattern | Fix |
|---|---|
| Wall of text | Split by idea, add headings, turn enumerations into lists |
| Preamble before the point ("In this document we will…") | Delete it; start with the point |
| Vague words ("simply", "just", "easily", "etc.", "various") | Remove them or name the items |
| Marketing tone, superlatives | State what it does and the measured figure |
| Duplicated content in several files | Keep one source, link to it |
| Stale content (old option names, removed commands) | Update in the same commit as the code (`rules/docs.md`) |
| Instructions mixed with explanations | Separate them (Diátaxis, [guide](types/guide.md)) |
| Screenshots of text or code | Use text: it can be searched, copied and diffed |
| Unexplained jargon or acronyms | Define at first use or link to the glossary |
| "TODO" or "TBD" left in a published document | Resolve it or track it in `TODO.md` |

## Changelog

The changelog is read by users deciding whether to upgrade. Keep it readable over years (format: `rules/changelog.md`, Keep a Changelog).

- **Written for users**, not for maintainers: describe the effect ("Commands now fail when the config file is missing"), not the implementation ("Refactor loader").
- **One line per entry**, imperative mood, starting with the affected command, option or area.
- **Grouped by type** (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`), **breaking changes first** in their group and flagged `**Breaking:**`, with the migration step or a link to it.
- **Link** the issue or pull request when it holds useful detail.
- **Curated, not a commit dump**: several commits for one change make one entry; internal changes (refactoring, CI, tests, typos) are left out unless they change what users get.
- **A short release summary** under the version heading when a release has a theme or more than about ten entries: one or two sentences on what matters most.
- **Never rewrite released sections**, except to fix a factual error; mention the correction in the next release.

## Review checklist

- [ ] The reader and the purpose are clear from the first paragraph
- [ ] The document type matches the need; no tutorial, reference and explanation mixed in one page
- [ ] Each section starts with its point
- [ ] Every command, code sample and link was run or followed
- [ ] Names, paths, options and versions match the repository
- [ ] One term per concept; acronyms defined
- [ ] No duplicated content; links point to the single source
- [ ] Nothing left the reader cannot act on: no TBD, no vague "etc."
- [ ] Diagrams have a text description and match the code
- [ ] The project's documentation tools pass, if it has any

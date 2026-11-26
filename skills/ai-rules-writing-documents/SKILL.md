---
name: ai-rules-writing-documents
description: "Use when writing or substantially revising a document: README, guide, specification, design document, ADR, changelog entry or diagram. Pick the document type, write for one reader, check the text against the review checklist."
---
# Writing documents

A document is read many more times than it is written. Write it for one reader with one purpose, put the point first, and check it before calling it done. Small updates that keep docs in sync with the code follow `rules/docs.md`; use this skill when a document is created or a section is rewritten.

## Procedure

1. **Name the reader and the purpose.** One sentence: who reads it (a new user, a contributor, a reviewer, the future maintainer) and what they must be able to do or decide afterwards. A document with two readers usually needs two documents.
2. **Pick the type** and read its reference. Each type has its own structure; mixing them is the most common cause of a hard-to-use document.

   | Need of the reader | Type | Reference |
   |---|---|---|
   | Know what the project is, install it, run it once | README | [readme](references/types/readme.md) |
   | Learn, do a task, look up a fact, understand a concept | Guide (Diátaxis) | [guide](references/types/guide.md) |
   | Agree on what to build and how to tell it is done | Specification | [spec](references/types/spec.md) |
   | Agree on how to build it, with the alternatives | Design document | [design-doc](references/types/design-doc.md) |
   | Record one decision and its reasons | ADR | `ai-rules-architecture-proposal` |
   | Know what changed in a release | Changelog | [quality](references/quality.md#changelog) and `rules/changelog.md` |

3. **Check the language.** Documents are in English unless the user explicitly chose another language for them, recorded in the `README.md` (`core/language.md`). Follow the recorded choice; never switch on your own.
4. **Outline first.** Write the headings and one line per section, and show the outline to the user for a new document of more than a page. Fixing the structure is cheap before the prose exists.
5. **Draft** following [quality](references/quality.md): point first, plain words, one term per concept, examples taken from the project.
6. **Add a diagram** only where a picture saves words: structure, flow, states, sequence. Diagrams as code, Mermaid by default, see [diagrams](references/diagrams.md).
7. **Verify.** Run every command and code sample you show, follow every link, check names and paths against the repository. A document that shows a command that fails is a bug.
8. **Review** with the checklist at the end of [quality](references/quality.md), and run the project's documentation tools if it has any ([tooling](references/tooling.md)). Do not add tools the project does not use without asking.

## Rules of thumb

- Shorter is better when nothing the reader needs is lost. Cut what the reader already knows or will never use.
- Document the why and the decisions; the code already says what it does.
- One source of truth per fact: link to it instead of copying it, so that it cannot drift.
- Write for a reader who skims: headings that say something, short paragraphs, lists and tables for parallel items.
- Never invent: a version, a figure, a behavior or a quotation that you did not check is marked as unverified or left out.

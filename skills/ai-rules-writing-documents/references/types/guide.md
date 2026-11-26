# Guides (Diátaxis)

User documentation serves four distinct needs. Each page serves one; mixing them makes every page worse. Organize `docs/` by these four types when the documentation grows beyond the README.

| Type | Reader's need | Form | Avoid |
|---|---|---|---|
| **Tutorial** | Learn, as a beginner | A lesson: a guided path to a working result, every step given, success guaranteed | Explanations, options, choices |
| **How-to guide** | Do a specific task, already competent | A recipe: the goal in the title ("How to rotate the token"), prerequisites, numbered steps, the expected result | Teaching basics, covering every case |
| **Reference** | Look up a fact while working | A description that mirrors the product: commands, options, config keys, API; complete, consistent, dry | Instructions, opinions |
| **Explanation** | Understand why | A discussion: background, design reasons, alternatives, trade-offs | Steps to follow, reference lists |

## Rules

- Title each page by its type: tutorials and how-to guides by the goal, references by the thing described, explanations by the topic ("About the project profile").
- Link across types instead of mixing: a how-to links to the reference for every option and to the explanation for the why.
- Generate the reference from the code when the tooling allows it (`--help`, docstrings, schemas), so that it cannot drift.
- Each how-to states its prerequisites and ends with how to check it worked.
- Start small: a tutorial-like quick start in the README and a reference page are often enough; add the other types when users ask the questions they answer.

Source: Diátaxis, Daniele Procida, <https://diataxis.fr/>.

---
name: ai-rules-releasing
description: "Use when preparing or publishing a release: decide the version from the changelog, release commit with VERSION and CHANGELOG, release and tag messages, tag, platform release with notes from the changelog, artifacts, then open the next -dev version."
---
# Releasing

A release turns `[Unreleased]` into a published version. Every step that publishes (commit, tag, push, platform release) is run or confirmed by the user; the agent prepares the files, the messages and the commands, and checks each result.

## 1. Decide the version

- Read `[Unreleased]` in `CHANGELOG.md` and propose the level (`rules/versioning.md`): any breaking change → MAJOR (before 1.0.0, MINOR), any addition → MINOR, fixes only → PATCH. Give the reason in one line and wait for the user's choice.
- Check that the tag does not exist yet (`git tag -l X.Y.Z`, and on the remote with `git ls-remote --tags <remote> X.Y.Z`).

## 2. Pre-release checklist

- All tests pass and CI is green on the commit the release starts from.
- `[Unreleased]` is complete and readable (`ai-rules-writing-documents`, changelog practices): breaking changes first with their migration step, no internal noise; add a short release summary under the version heading when the release has a theme or many entries.
- Review workflow permissions, action pins, and external downloads used in CI (see `rules/ci.md`).
- `README.md` matches the release (version-specific instructions, measured figures).

## 3. Release commit

- Strict profile: commit on a `release/X.Y.Z` branch and merge through a PR (see `core/git.md`). Light profile: the release commit may go directly on `main`.
- Set `VERSION` to the final `X.Y.Z` (dropping the `-dev` suffix) in the release commit only.
- Update `CHANGELOG.md`: rename `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD` and add a new empty `[Unreleased]` section; update the comparison links at the bottom if the file has them.
- Commit message: `chore(release): bump version to X.Y.Z`, written to `.private/COMMIT_MESSAGE`.
- Wait for explicit user validation before committing and tagging; give the command block (`ai-rules-finishing-a-branch`).

## 4. Release and tag messages

- Before any release action, draft a detailed release message covering: summary of changes, breaking changes (if any), migration steps (if any), notable fixes. Write it to `.private/RELEASE_MESSAGE` (create if absent, overwrite if present) and present it to the user for review before using it in the platform release.
- Write the tag message to `.private/TAGGING_MESSAGE`: the version and the release summary in a few lines.
- No attribution line in release and tag messages (see `core/commits.md`).

## 5. Tag

- Tag format: `X.Y.Z` (no `v` prefix), must match the content of `VERSION`.
- Tag only the release commit once it is on `main` and CI is green on it (`core/git.md`): after the merge, `git checkout main`, `git pull`, and check `cat VERSION` and the CI status of `HEAD`.
- Annotated, signed when the user signs commits; push only after user confirmation:

```bash
git tag -s X.Y.Z -F .private/TAGGING_MESSAGE    # -a instead of -s without a signing key
git push <remote> X.Y.Z
```

## 6. Platform release

Create the platform release **after** the tag has been pushed, with the corresponding `CHANGELOG.md` section as notes, extracted by [`scripts/extract-changelog.sh`](scripts/extract-changelog.sh) from this skill's folder (it reads `CHANGELOG.md` in the current directory).

GitHub:

```bash
gh release create X.Y.Z \
  --title "X.Y.Z" \
  --notes-file <(<skill-dir>/scripts/extract-changelog.sh X.Y.Z) \
  --verify-tag \
  --latest
```

Forgejo, with the `tea` CLI (https://gitea.com/gitea/tea):

```bash
tea releases create \
  --tag X.Y.Z \
  --title "X.Y.Z" \
  --note "$(<skill-dir>/scripts/extract-changelog.sh X.Y.Z)"
```

Without `tea`, the REST endpoint is `POST https://<forgejo-host>/api/v1/repos/<owner>/<repo>/releases` with `tag_name`, `name`, `body`, `draft` and `prerelease`, and a token from the environment (`Authorization: token $FORGEJO_TOKEN`), never written in a file or a command line that gets saved.

Use the release message of step 4 instead of the extracted notes when the user prefers it.

## 7. Artifacts

- Package and attach release artifacts if applicable (e.g. `.tar.gz` archive), with their checksums.
- GitHub: add artifact paths as additional arguments to `gh release create`.
- Forgejo: use `tea releases assets create` or the API endpoint `POST /repos/{owner}/{repo}/releases/{id}/assets`.

## 8. Open the next version

In the first commit after the release, set `VERSION` to the next planned version with the `-dev` suffix (`X.Y.Z-dev`, `rules/versioning.md`), on its own branch in the strict profile. Then check that the release page, the tag and `VERSION` agree, and propose cleaning `.private/RELEASE_MESSAGE` and `.private/TAGGING_MESSAGE`.

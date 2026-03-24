# Release Workflow

## Pre-release checklist
- Ensure all tests pass and CI is green
- Bump the `VERSION` file (follow semver rules from `versioning.md`)
- Update `CHANGELOG.md` with the release notes for this version
- Verify the tag does not already exist

## Release commit
- Commit message: `chore(release): bump version to X.Y.Z`
- Wait for explicit user validation before committing and tagging

## Tagging
- Tag format: `X.Y.Z` (no `v` prefix), must match the content of `VERSION`
- Push the tag only after user confirmation

## Platform release
Create a release on the appropriate platform using the `X.Y.Z` tag and the corresponding `CHANGELOG.md` section as release notes:
- **Forgejo** — create release via Forgejo UI or API
- **GitHub** — create release via `gh release create`

## Artifacts
- Package and attach release artifacts if applicable (e.g. `.tar.gz` archive)

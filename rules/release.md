# Release Workflow

## Pre-release checklist
- Ensure all tests pass and CI is green
- Bump the `VERSION` file (follow semver rules from `versioning.md`)
- Update `CHANGELOG.md`: rename `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD` and add a new empty `[Unreleased]` section
- Verify the tag does not already exist

## Release commit
- Commit message: `chore(release): bump version to X.Y.Z`
- Wait for explicit user validation before committing and tagging

## Tagging
- Tag format: `X.Y.Z` (no `v` prefix), must match the content of `VERSION`
- Push the tag only after user confirmation:
  ```bash
  git tag X.Y.Z
  git push origin X.Y.Z
  ```

## Platform release

Create the platform release **after** the tag has been pushed. Use the corresponding `CHANGELOG.md` section as release notes.

### GitHub

```bash
gh release create X.Y.Z \
  --title "X.Y.Z" \
  --notes-file <(scripts/extract-changelog.sh X.Y.Z) \
  --latest
```

### Forgejo

Using the `tea` CLI (install: `tea` from https://gitea.com/gitea/tea):

```bash
tea releases create \
  --tag X.Y.Z \
  --title "X.Y.Z" \
  --note "$(scripts/extract-changelog.sh X.Y.Z)"
```

Alternatively, via the Forgejo REST API:

```bash
curl -s -X POST "https://<forgejo-host>/api/v1/repos/<owner>/<repo>/releases" \
  -H "Authorization: token $FORGEJO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tag_name": "X.Y.Z",
    "name": "X.Y.Z",
    "body": "<release notes>",
    "draft": false,
    "prerelease": false
  }'
```

## Artifacts
- Package and attach release artifacts if applicable (e.g. `.tar.gz` archive)
- GitHub: add artifact paths as additional arguments to `gh release create`
- Forgejo: use `tea releases assets create` or the API endpoint `POST /repos/{owner}/{repo}/releases/{id}/assets`

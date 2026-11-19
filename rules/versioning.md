# Semantic Versioning

All projects follow semver (`MAJOR.MINOR.PATCH`):

- **PATCH** — backwards-compatible bug fixes
- **MINOR** — new backwards-compatible functionality
- **MAJOR** — breaking changes

Bump `VERSION` only in the release commit (see `release.md`), never in feature or fix commits. Between releases, `VERSION` holds the next planned version with a `-dev` suffix (`X.Y.Z-dev`), set in the commit that opens that version; the release commit removes the suffix. Record the change in `CHANGELOG.md` `[Unreleased]`; the bump level (PATCH/MINOR/MAJOR) is decided at release from its content.

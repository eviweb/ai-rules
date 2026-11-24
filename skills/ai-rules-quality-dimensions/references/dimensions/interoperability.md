# Interoperability
The system exchanges data with other systems and coexists with them without friction.

- Prefer open standards and formats; document contracts (OpenAPI, JSON Schema, file formats) and version them
- Be strict in what you emit and validate what you accept at the boundary
- Coexist: no clashes on ports, files, names or global state with other software on the same machine
- Provide import and export so users are not locked in
- Test against the real counterpart, or a contract test, not only against a mock

Red flags: proprietary formats without export, undocumented wire formats, breaking changes without a version, hardcoded assumptions about the other side.

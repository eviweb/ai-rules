# Security
The system protects its data, users, and infrastructure from misuse and attack.

- Never hardcode credentials or secrets — use env vars or a secret manager
- Validate and sanitise all external input to prevent injection
- Apply least privilege: request only the permissions strictly needed
- Keep dependencies up to date and audit them regularly
- See `core/security.md` for patterns; threat modelling, OWASP and supply chain: [security by design](../contexts/security-by-design.md)

Red flags: secrets in source, world-writable files, unvalidated input passed to shell commands or SQL, overly broad permissions.

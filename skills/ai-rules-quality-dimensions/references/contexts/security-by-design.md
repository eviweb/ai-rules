# Security by design

Read when the project is reachable over a network, handles authentication, secrets or untrusted input, or depends on third-party packages. The always-loaded basics are in `core/security.md`; this adds design-time practice.

## Design principles (Saltzer and Schroeder)

- **Economy of mechanism**: keep the security-relevant code small and simple.
- **Fail-safe defaults**: deny unless explicitly allowed.
- **Complete mediation**: check authorization on every access, not once at the door.
- **Open design**: security does not depend on the design being secret.
- **Separation of privilege**: sensitive actions need more than one condition.
- **Least privilege** and **least common mechanism**: minimum rights, minimum shared state.
- **Psychological acceptability**: secure paths must be easy to use, or people bypass them.
- Also: **defense in depth**, **secure by default**, fail securely (an error must not open access), assume the network and the client are hostile.

## Threat modelling (small, at design time)

Answer Shostack's four questions on a one-page data-flow diagram: what are we working on, what can go wrong, what are we going to do about it, did we do a good job. Use **STRIDE** to prompt: spoofing, tampering, repudiation, information disclosure, denial of service, elevation of privilege. Record the threats and decisions in the design document or an ADR.

## Checklists

- **OWASP Top 10** (web, 2025 edition), **OWASP API Security Top 10** (APIs, 2023 edition), **OWASP ASVS** (verification levels, version 5.0) as the reference lists; name the ones that apply and the edition used.
- **Input**: validate against an allow-list at the boundary; encode on output; parameterized queries; never build shell commands from untrusted text.
- **Identity**: central authentication and authorization, deny by default, session expiry, multi-factor where it matters; vetted libraries, never homemade cryptography.
- **Secrets**: never in the repository; rotate; scan history (`gitleaks`, `trufflehog`).
- **Supply chain**: pin and audit dependencies, verify signatures and checksums, pin CI actions to a SHA (`rules/ci.md`), keep an SBOM when the project is distributed; consider build provenance (SLSA).
- **Exposure**: rate limiting and size limits (`rules/api.md`), security headers, least-privileged service accounts, no debug endpoints in production.
- **Detection**: log security events without secrets or personal data; alert on them; plan the response to an incident and to a leaked secret.

## Tools to propose (not to add silently)

`semgrep`, `bandit` (Python), `gosec` (Go), `cargo audit` and `cargo deny` (Rust), `composer audit` (PHP), `npm audit` or `osv-scanner`, `trivy` (containers), `gitleaks`.

## Red flags

Authorization checked only in the user interface, secrets in environment dumps or logs, wildcard permissions, dependencies never updated, "internal only" used as a reason to skip authentication.

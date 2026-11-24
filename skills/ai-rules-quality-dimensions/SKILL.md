---
name: ai-rules-quality-dimensions
description: "Use when designing a project or a significant change, or judging its quality: pick the critical dimensions (based on ISO/IEC 25010: correctness, reliability, security, privacy, accessibility, evolvability...) and record the trade-offs."
---
# Project Quality Dimensions

Design every project with the applicable dimensions below in mind from the start, not retrofitted. At kickoff, identify which dimensions are critical for the use case, tell the user, and document any conscious trade-off. The list follows ISO/IEC 25010 (2023) with a few additions; the mapping is in [iso-25010](references/iso-25010.md).

| Dimension | What it asks |
|-----------|--------------|
| [Correctness](references/dimensions/correctness.md) | Does what was asked, completely, and solves the real problem |
| [Reliability](references/dimensions/reliability.md) | Delivers correct service continuously: availability, recovery, data integrity |
| [Robustness](references/dimensions/robustness.md) | Survives invalid input and unexpected conditions |
| [Resilience](references/dimensions/resilience.md) | Keeps working, possibly degraded, when a dependency fails |
| [Security](references/dimensions/security.md) | Protects data, users and infrastructure from misuse |
| [Privacy & data minimisation](references/dimensions/privacy.md) | Collects and keeps only the data strictly needed |
| [Safety](references/dimensions/safety.md) | Avoids states that could harm people, property or the environment |
| [Performance](references/dimensions/performance.md) | Responds within acceptable time and resource bounds |
| [User-friendliness](references/dimensions/user-friendliness.md) | Easy to use correctly, hard to use incorrectly |
| [Accessibility](references/dimensions/accessibility.md) | Usable by people with different abilities, devices and situations |
| [Maintainability](references/dimensions/maintainability.md) | Understandable and changeable by anyone who knows the language |
| [Evolvability](references/dimensions/evolvability.md) | Absorbs change at low cost over years |
| [Testability](references/dimensions/testability.md) | Behaviour can be verified automatically and reliably |
| [Observability](references/dimensions/observability.md) | Behaviour can be understood in production without redeploying |
| [Auditability](references/dimensions/auditability.md) | Actions are traceable: who, what, when, result |
| [Portability](references/dimensions/portability.md) | Works across all declared target environments |
| [Interoperability](references/dimensions/interoperability.md) | Exchanges data with other systems and coexists with them |

Each dimension links to its own file with goals, practices and red flags. Read only the files of the dimensions that apply.

## Contexts: read only what the project needs

Some concerns need a deeper checklist. Read the file when its condition holds, and skip it otherwise.

| Read | When the project... |
|------|---------------------|
| [accessibility](references/contexts/accessibility.md) | has any interface: web, GUI, TUI or CLI, documentation, error output |
| [privacy by design](references/contexts/privacy-by-design.md) | handles personal data (accounts, emails, IP addresses, logs with identifiers) |
| [security by design](references/contexts/security-by-design.md) | is reachable over a network, handles authentication, secrets or untrusted input, or has third-party dependencies |
| [user-centric design](references/contexts/user-centric.md) | has end users, including developers using a CLI or an API |
| [evolvability](references/contexts/evolvability.md) | is meant to live beyond a one-off: debt, decisions, deprecation |

When these contexts apply, they also become criteria of the architecture comparison (`ai-rules-architecture-proposal`).

---
name: ai-rules-quality-dimensions
description: "Use when designing a project or a significant change, or judging its quality: robustness, security, performance, extensibility, usability, maintainability, observability, testability, portability, auditability, privacy, resilience."
---
# Project Quality Dimensions

Design every project with the applicable dimensions below in mind from the start, not retrofitted. At kickoff, identify which dimensions are critical for the use case and document any conscious trade-off.

| Dimension | What it asks |
|-----------|--------------|
| Robustness | Survives failures, invalid input and unexpected conditions |
| Security | Protects data, users and infrastructure from misuse |
| Performance | Responds within acceptable time and resource bounds |
| Extensibility | Accepts new requirements without rewrites |
| User-friendliness | Easy to use correctly, hard to use incorrectly |
| Maintainability | Understandable and changeable by anyone who knows the language |
| Observability | Behaviour can be understood in production without redeploying |
| Testability | Behaviour can be verified automatically and reliably |
| Portability | Works across all declared target environments |
| Auditability | Actions are traceable: who, what, when, result |
| Privacy & data minimisation | Collects and keeps only the data strictly needed |
| Resilience | Keeps working, possibly degraded, when a dependency fails |

For the goals, practices and red flags of each dimension that applies, read [the full guidance](references/dimensions.md). Read only the sections of the dimensions that apply to the project.

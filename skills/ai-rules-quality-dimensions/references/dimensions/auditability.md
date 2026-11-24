# Auditability
Actions taken by the system are traceable — who did what, when, and with what result.

- Log all state-changing operations with enough context to reconstruct the sequence of events
- Include actor identity (user, service, API key ID) in log entries for authenticated systems
- Never log sensitive data (passwords, tokens, PII) — log identifiers, not values
- Retain audit logs separately from application logs, with a longer retention period
- For CLIs: log commands and their outcomes to the state log file

Red flags: no record of what changed and when, logs that are overwritten or rotated too aggressively, audit and debug logs mixed in the same stream.

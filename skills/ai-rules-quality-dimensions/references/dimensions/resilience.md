# Resilience
The system continues to function — possibly in a degraded mode — when a dependency or component fails.

- Identify single points of failure at design time and document mitigation strategies
- Implement timeouts on all external calls — never wait indefinitely
- Use retries with exponential backoff for transient failures; set a maximum retry budget
- Design for partial availability: if a non-critical dependency is down, degrade gracefully rather than failing entirely
- Test failure scenarios explicitly (dependency unavailable, timeout, malformed response)

Red flags: no timeouts on HTTP calls, infinite retry loops, cascading failures when one service goes down, no graceful degradation path documented.

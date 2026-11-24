# Observability
The system exposes enough information to understand its behaviour in production without modifying or redeploying it.

- Log meaningful events at the right level (see `rules/logging.md`)
- Expose a health check endpoint for services (`/health` or `/healthz`)
- Emit metrics for key operations: request count, error rate, latency, queue depth
- Use structured logs with a consistent schema so they can be queried
- In distributed systems: propagate a `trace_id` / `request_id` across service calls

Red flags: no logs in production paths, logs that say "error occurred" without context, no way to check if the service is healthy, metrics only on happy paths.

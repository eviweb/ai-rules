# Reliability
The system delivers correct service continuously over time.

- Set availability and recovery targets at design time, even informal ones (how long may it be down, how much data may be lost)
- Make recovery routine: backups that are restored in a test, rollback for every deployment and migration
- Health checks and alerts on what users feel, not only on processes
- Fix known failure modes at the cause; track repeated incidents
- Protect data integrity: transactions, idempotent operations, checksums where corruption matters
- Distinct from robustness (bad input) and resilience (failing dependencies): this is the long-run behaviour of the whole system
- Practice from site reliability engineering, scaled to the project (below): an SLI measures it, an SLO sets the target, the error budget says how much failure is acceptable before reliability work takes priority
- Write a short runbook for the failures you expect (what to check, what to run, who to ask), and a blameless post-mortem after an incident
- Remove single points of failure, test failures on purpose (stop a dependency, restore a backup, roll back), and test capacity before the load arrives
- Watch the four golden signals (latency, traffic, errors, saturation); separate liveness from readiness probes; roll out progressively (canary) with a quick rollback
- Track the failed deployment recovery time and the change fail rate, two of the five DORA metrics (see [evolvability](../contexts/evolvability.md))

Red flags: backups never restored, no rollback plan, no stated availability target, the same incident twice, silent data corruption possible.

| Project | Minimum expected |
|---------|------------------|
| Personal tool or script | One sentence on what must keep working, a restore that was tested, a way back from a bad change |
| Internal or shared service | A simple SLO, a short runbook, health checks, backups restored in a test |
| Public service | SLO with an error budget, post-mortems, failure tests, progressive rollout |

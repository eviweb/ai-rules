# Architecture catalogue

Candidates to start from. Each entry: what it is, when it fits, when to avoid it, what it costs, how reversible it is. Adapt, combine and rename freely; the aim is a fair comparison, not a pick-list.

## Single script or module
- Shape: one file or one small package, functions only.
- Fits: scripts, one-off tools, prototypes, a single user.
- Avoid when: several contributors, several interfaces, logic that must be reused.
- Costs: refactoring when it grows; little structure to lean on.
- Reversibility: high.

## Library plus thin CLI
- Shape: logic in an importable library, a small command layer over it.
- Fits: tools used from the shell and from other code; easy testing of the core.
- Avoid when: nothing will ever reuse the logic and a script is enough.
- Costs: two layers to keep consistent.
- Reversibility: high.

## Layered
- Shape: presentation, application, data layers; each depends on the next one down.
- Fits: CRUD-style applications, familiar to most teams.
- Avoid when: rich domain rules end up scattered across layers, or layers only forward calls.
- Costs: boilerplate; the data layer tends to shape everything.
- Reversibility: medium.

## Modular monolith
- Shape: one deployable, internally split into modules with explicit boundaries and public interfaces.
- Fits: products that may grow, small teams, one database.
- Avoid when: the boundaries are unknown (draw them after the first working slice).
- Costs: discipline to keep the boundaries (check them automatically).
- Reversibility: high; a good first step before any split into services.

## Hexagonal (ports and adapters) and clean architecture
- Shape: domain core with no outward dependency; ports define what it needs; adapters connect I/O, storage, interfaces.
- Fits: rich domain rules, several adapters (CLI and API, several storage backends), heavy testing without I/O.
- Avoid when: little domain logic, one interface, one storage: it adds indirection for nothing.
- Costs: more files and mapping code; the team must hold the dependency rule.
- Reversibility: medium; swapping adapters is cheap, changing the core is not.

## Pipes and filters
- Shape: small stages that read a stream and write a stream, composed in sequence.
- Fits: shell tools, text and data transformation, batch processing.
- Avoid when: stages need rich shared state or interactive control.
- Costs: error handling across stages; format agreements between them.
- Reversibility: high.

## Plugin or registry (microkernel)
- Shape: a small core and extensions registered by name or configuration (`agents.toml` is one).
- Fits: many similar variants (agents, formats, providers) added over time.
- Avoid when: two variants that will not grow.
- Costs: a stable extension contract to maintain and version.
- Reversibility: medium.

## Client-server application (server-rendered or API plus client)
- Shape: a server owning data and rules, clients over HTTP.
- Fits: multi-user applications, shared data, web interfaces.
- Avoid when: a local single-user tool.
- Costs: authentication, deployment, availability, security exposure.
- Reversibility: medium.

## Rich client (GUI or TUI) with separated presentation
- Shape: view, plus a model or view-model that holds state and logic (MVC, MVP, MVVM).
- Fits: interactive interfaces; keeps logic testable without the screen.
- Avoid when: a form that submits once.
- Costs: binding code; accessibility to design in from the start.
- Reversibility: medium.

## Event-driven and message-based
- Shape: components communicate through events or queues; handlers react.
- Fits: loose coupling, asynchronous work, integration of independent systems, bursts.
- Avoid when: a simple request and response is enough, or strict ordering and immediate consistency are needed.
- Costs: harder debugging and tracing, eventual consistency, a broker to run.
- Reversibility: low to medium.

## Microservices
- Shape: independently deployable services, each owning its data.
- Fits: several teams, independent scaling and release cycles, strong isolation.
- Avoid when: one team, unclear boundaries, early stage: the default for most projects is a modular monolith.
- Costs: distributed systems problems, network failures, versioned contracts, observability, operations.
- Reversibility: low.

## Serverless functions
- Shape: small functions triggered by events or requests on a managed platform.
- Fits: spiky or low traffic, glue code, no servers to run.
- Avoid when: long-running work, strict latency, platform lock-in is unacceptable.
- Costs: cold starts, local testing, vendor lock-in, limits.
- Reversibility: medium.

## Batch or ETL pipeline
- Shape: scheduled jobs moving and transforming data between stores.
- Fits: reporting, migrations, data synchronization.
- Avoid when: users need results immediately.
- Costs: scheduling, retries, idempotency, monitoring of silent failures.
- Reversibility: high.

## Static site or generated output
- Shape: content built ahead of time and served as files.
- Fits: documentation, sites without per-user content.
- Avoid when: personalization or frequent writes by users.
- Costs: build step; dynamic needs pushed to external services.
- Reversibility: high.

## Data streaming pipeline
- Shape: continuous processing of events through stages (ingest, transform, sink) with a broker or stream engine.
- Fits: near-real-time analytics, monitoring feeds, sustained high event rates.
- Avoid when: periodic batches are enough, or volumes are small: a scheduled job is far simpler.
- Costs: operating the stream infrastructure, ordering and exactly-once questions, replay and backfill.
- Reversibility: medium.

## Local-first or offline-first application
- Shape: the device holds the data and works without a network; synchronization is a background concern.
- Fits: mobile and desktop tools, unreliable networks, user-owned data, privacy.
- Avoid when: data must be strongly consistent between many writers at once.
- Costs: conflict resolution, sync protocol, schema migration on devices.
- Reversibility: low to medium.

## Strangler migration (transitional)
- Shape: new behavior is built beside the old system and requests move over piece by piece until the old one can be removed.
- Fits: replacing or restructuring a system that must keep running; the usual route for a large refactoring.
- Avoid when: the old system is small enough to rewrite in one safe step.
- Costs: running two systems for a while, a routing layer, discipline to finish the removal.
- Reversibility: high at each step.

## Not recommended by default

Know the name and the cost; recommend only with evidence of the need, and write the evidence in the ADR.

- **CQRS**: separate read and write models; fits very different read and write loads; doubles the model and adds synchronization.
- **Event sourcing**: state kept as the log of events; fits audit-critical domains with replay; heavy to query, evolve and operate.
- **Service mesh**: a network layer for service-to-service concerns; fits large service fleets; high operational weight.
- **Multi-cloud**: running across providers; fits strict regulatory or availability needs; large cost for rarely used portability.

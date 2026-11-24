# Criteria for comparing architectures

Keep six to ten, chosen for the project. Rate each candidate against each criterion; explain the surprising ratings.

## Always present

| Criterion | The question |
|-----------|--------------|
| Effort to build | How long to the first useful release? |
| Running cost and operational burden | What does it cost to host, monitor, upgrade and be on call for? |
| Reversibility | How hard is it to move away from this choice later? |
| Testability | Can the core be tested without the network, the disk and the clock? |
| Fit with the team | Does the team (or the user) know it well enough to maintain it? |

## Chosen from the context of the project

| Criterion | Comes from | Typical question |
|-----------|-----------|------------------|
| Domain complexity | the problem | Many business rules and states, or mostly plumbing? |
| Expected lifetime and rate of change | evolvability | A one-off, or years of changes? |
| Number of integrations and adapters | interoperability | How many external systems, interfaces, storage backends? |
| Interface type | accessibility, user-centric | CLI, TUI, GUI, web, API, library? Which assistive needs? |
| Data volume and throughput | performance | Kilobytes or terabytes? Requests per second? |
| Latency sensitivity | performance | Does a hundred milliseconds matter? |
| Availability and recovery | reliability | What may be down, for how long, with how much data loss? |
| Security and privacy exposure | security by design, privacy by design | Untrusted input, personal data, secrets, public network? |
| Target environments | portability | Ubuntu LTS, Termux, containers, several shells? |
| Safety of effects | safety | Does it delete data or change production? |
| Independence of parts | evolvability | Must parts deploy, scale or be owned separately? |
| Observability needs | observability | Must behaviour be understood in production? |

## Size classes (a starting point, not a verdict)

Classify by signals, never by the number of lines.

| Class | Signals | Usual first candidates |
|-------|---------|------------------------|
| Script | one interface, one storage, one contributor, short life | single script or module |
| Tool | one or two interfaces, a few modules, one or two contributors | library plus thin CLI; layered |
| Product | several interfaces or storage backends, rich domain rules, several contributors, long life | modular monolith; hexagonal |
| Platform | several teams, independent deployment or scaling, strong isolation required | services, event-driven, only with the evidence |

Move up a class only when a criterion forces it, and say which one.

## Rough numbers

When load or cost matters, do a back-of-the-envelope estimate (requests per second, data per day, storage after a year, monthly cost) for each candidate. An order of magnitude is enough to discard an option.

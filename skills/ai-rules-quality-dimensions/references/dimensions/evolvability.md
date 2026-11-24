# Evolvability
The system absorbs change at low cost over years: new requirements, new dependencies, retirements.

- Separate concerns: each module has one reason to change; depend on abstractions, inject dependencies
- Avoid hardcoded assumptions about the number of items, types, or destinations (e.g. hardcoding agent names instead of reading from config)
- Design for the current requirements; leave extension points only where growth is certain, and document them in `README.md`
- Keep the cost of change visible: files that change most (hotspots), a technical-debt register, decisions recorded as short ADRs
- Protect architectural properties with automated checks (import contracts, size budgets, coverage floors) so they cannot erode silently
- Evolve contracts with a deprecation path: announce, warn, remove after a stated number of versions (expand and contract)
- Details and checklists: [evolvability](../contexts/evolvability.md)

Red flags: God classes, feature flags proliferating across the codebase, copy-paste instead of abstraction, tight coupling between unrelated modules, decisions nobody can explain, upgrades postponed until they are painful.

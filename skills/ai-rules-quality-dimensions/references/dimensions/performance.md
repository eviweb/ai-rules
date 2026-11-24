# Performance
The system responds within acceptable time and resource bounds under expected load.

- Define performance targets at project start (response time, throughput, memory budget)
- Measure before optimising — never optimise based on intuition alone
- Avoid unnecessary I/O in hot paths; prefer lazy loading over eager loading
- Cache results that are expensive to compute and stable enough to cache safely
- Profile under realistic load, not synthetic microbenchmarks alone

Red flags: N+1 queries, unbounded loops over external data, synchronous blocking in async contexts, caches with no invalidation strategy.

# JavaScript and TypeScript

## Idioms
- TypeScript `strict`; discriminated unions for states; `readonly` and immutable updates; no `any` at boundaries (`unknown` plus narrowing).
- `async/await` with errors handled at the boundary; small pure functions; ES modules; one component, one job.

## Signals
- Callback pyramids, unhandled promises, `any` spreading through the code, `==`, boolean props that switch behavior.
- Giant components or files, mutation of props or shared state, deeply nested ternaries.

## Detectors
- `eslint` with `complexity`, `max-depth`, `max-params`, `eslint-plugin-sonarjs` (cognitive complexity), `typescript-eslint`; `tsc --noEmit`; `prettier`.
- `knip` (unused files, exports, dependencies), `dependency-cruiser` or `madge` (cycles and layer rules), `jscpd` (duplication).
- `vitest` or `jest` with coverage; `stryker` (mutation testing).
- Automated rewrites: `jscodeshift`, `ts-morph`, editor rename and extract.

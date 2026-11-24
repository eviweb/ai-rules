# Go

## Idioms
- Small interfaces defined where they are used; accept interfaces, return structs.
- Errors are values: wrap with `%w`, check with `errors.Is` and `errors.As`; pass `context.Context` first.
- Composition by embedding; table-driven tests; `gofmt` and `goimports` always.

## Signals
- Large interfaces, `any` or `interface{}` in APIs, ignored errors, `panic` for expected failures.
- Package-level mutable state, `init()` with side effects, goroutines with no way to stop (leaks).

## Detectors
- `go vet`, `staticcheck`, `golangci-lint` (enable `gocyclo`, `gocognit`, `dupl`, `unused`, `errcheck`), `go test -race -cover`.
- `gopls` for rename, extract and move; `gorename`-style changes through the language server.
- Mutation testing: `go-mutesting`, where the project accepts it.

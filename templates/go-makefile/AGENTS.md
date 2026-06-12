# AGENTS.md (Go — msgvault-style)

Copy and adapt from [endolith/msgvault](https://github.com/endolith/msgvault). You do not need to know Go deeply; follow existing patterns.

## Required workflow

1. Branch `cursor/<topic>-6eeb`.
2. Code changes include `*_test.go` coverage.
3. Run `make test` and `make lint` (or `make fmt` + `go vet`) until green.
4. Commit, push, open PR. **Do not merge.**

## Commands

```bash
make test      # preferred — includes correct build tags
make lint
make fmt
go vet ./...
```

msgvault requires `-tags "fts5 sqlite_vec"` for tests; this repo may differ — **read its Makefile**.

## Testing

- Use `github.com/stretchr/testify` (`require` / `assert`).
- Equality: `assert.Equal(t, want, got)` — want first.
- Do not add `t.Errorf` / `t.Fatal` in new tests.

## References in msgvault

- `AGENTS.md` — testify rules, build tags
- `CLAUDE.md` — architecture, `make` targets, commit every turn
- `.github/workflows/ci.yml` — test matrix, postgres job pattern

## Cursor Cloud

```json
{
  "install": "make build",
  "start": "echo ready"
}
```

Adjust if the project needs CGO or apt packages (msgvault uses DuckDB/SQLite).

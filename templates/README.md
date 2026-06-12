# Agent & CI templates for endolith repos

Shared scaffolding for Cloud Agents and GitHub Actions. **Not specific to
clone-and-add-forks** — this folder lives here until `endolith/agent-templates`
exists as its own repo (create it on GitHub and move this tree).

## Philosophy

- **Lint:** `ruff` only (no Black — it mangles NumPy arrays and similar).
- **Test:** `pytest` for Python; `make test` for Go (msgvault style).
- **Agent rules:** live in each repo's `AGENTS.md` so you don't repeat them in prompts.
- **Pro plan:** no Bugbot, no Teams-only autofix; CI + in-repo instructions only.

## Templates

| Directory | Use for |
|-----------|---------|
| `python-ruff-pytest/` | Hatchling/pip libraries (elsim, bipolar, cyclic-noise, BSS_DUET) |
| `go-makefile/` | Go binaries (msgvault pattern) |
| `json-adblock/` | Adblock Plus filter lists (clickbait) |
| `ahk-v1-windows/` | AutoHotkey v1 scripts (GridMove, AutoCorrect) |

## Roll out to a repo

1. Copy template files into the target repo (adjust names/paths).
2. Edit `AGENTS.md` — set default branch, install command, test extras.
3. Open PR; agent or human merges when green.

### One-line agent prompt

```
Copy templates/python-ruff-pytest/ from endolith/clone-and-add-forks (branch
cursor/agent-templates-6eeb) into <REPO>. Adapt AGENTS.md and CI for that
repo. Add smoke tests. Branch cursor/agent-infra-<name>-6eeb. Do not merge.
```

## Mimicking msgvault (Go)

msgvault's pattern (you don't need to know Go to copy the *shape*):

- `Makefile` with `test`, `lint`, `fmt` targets
- `AGENTS.md` + `CLAUDE.md` with "always commit", testify rules, build tags
- `.github/workflows/ci.yml` calling `make test` and `make lint`
- Pre-commit via `prek` / `make install-hooks` (optional)

See `templates/go-makefile/` for a minimal skeleton and pointers to msgvault.

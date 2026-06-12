# AGENTS.md

Instructions for Cloud Agents and other AI tools working in this repository.

## Required workflow

1. Branch: `cursor/<topic>-6eeb` off the default branch.
2. **Behavior changes include tests** in the same PR.
3. Run local CI commands below; **fix and push until green** before marking ready.
4. Commit and push incrementally. Open/update PR. **Do not merge.**

## Local CI

```bash
pip install -e ".[test]"
ruff check .
pytest
```

Adjust extras if this repo uses `[dev]` or `[examples]` instead of `[test]`.

## Lint

- **Use ruff.** Do not run Black (it reformats NumPy arrays and numeric code poorly).
- Blocking subset (if `ruff.toml` exists): `ruff check --select=E9,F63,F7,F82 .`
- Full check: `ruff check .`

## Tests

- Use **pytest**. Add regression tests for bugs; table-driven where appropriate.
- Mark API/network tests: `@pytest.mark.integration` and run default suite without them.
- No real API keys in unit tests — mock external calls.

## PR checklist

- [ ] Tests added or updated
- [ ] `ruff check .` passes
- [ ] `pytest` passes
- [ ] PR description states what changed and how to verify

## Cursor Cloud

- Install: `pip install -e ".[test]"` (see `.cursor/environment.json` if present)
- Ensure `~/.local/bin` is on `PATH` for `pytest` and `ruff`

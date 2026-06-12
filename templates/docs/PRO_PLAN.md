# Pro plan: what works without extra cost

| Feature | Pro | Notes |
|---------|-----|-------|
| Cloud Agents | Yes | Uses monthly credits |
| `AGENTS.md` in repo | Yes | Agents read automatically |
| GitHub Actions CI | Yes | Free for public repos |
| Cursor Automations | Check dashboard | May be available on Pro — optional |
| Bugbot | Extra $ | Skip |
| Auto-fix CI on agent PRs | Teams | Skip — use `AGENTS.md` "fix until green" |
| Cursor CLI in GHA | Uses API credits | Optional later |

## What actually works on Pro

1. **Deterministic CI** (ruff + pytest) on every PR
2. **`AGENTS.md`** so agents self-instruct without you repeating rules
3. **Cloud Agents** that read `AGENTS.md` and push until CI passes (when you tell them to in the file)
4. Comment `@cursor fix CI` on a PR (manual, uses credits)

## open-interpreter and Poetry

`open-interpreter` has PEP 621 `pyproject.toml` but legacy `[tool.poetry]` and CI that runs `poetry install`. **You can use pip:**

```bash
pip install -e ".[server]"
pytest
```

An agent should migrate CI to `pip install -e ".[test]"` or similar — no Poetry required.

## elsim PR #42 AGENTS.md

That PR is **useful** — keep it. It documents pip install, ruff subsets, pytest, Numba caveat, PATH. Merge #42 or copy `templates/python-ruff-pytest/AGENTS.md` and add elsim-specific extras (`[fast]`, examples).

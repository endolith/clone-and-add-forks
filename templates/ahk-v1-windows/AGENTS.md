# AGENTS.md

AutoHotkey **v1** script(s). CI only checks syntax on Windows runners.

## Workflow

1. Branch `cursor/<topic>-6eeb`.
2. Match existing AHK version (v1 `:=` vs v2 `#Requires AutoHotkey v2.0`).
3. Manual test on Windows required for behavior; CI is syntax-only.

## Local test (Windows)

Run the script with AutoHotkey v1.1 — there is no pytest equivalent.

## CI

`.github/workflows/ahk-syntax.yml` uses `windows-latest` and AutoHotkey to compile/check syntax.

## Notes

- GridMove uses **AHK v1** syntax.
- For v2 scripts, use `#Requires AutoHotkey v2.0` and v2 function syntax.

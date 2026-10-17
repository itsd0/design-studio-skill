# Contributing

## What lands

- Design-system changes (`SKILL.md`, `references/`, `assets/`) with before/after rationale.
- Linter rules in `scripts/lint.py`, each with a fixture in `tests/fixtures/` and a case in `tests/run_tests.py`.
- Demo artifacts that pass `scripts/lint.py` with zero P0/P1.

## Required checks (run before every PR)

```bash
python3 tests/run_tests.py
python3 scripts/lint.py index.html assets/*.html demo/*.html
```

Both must pass: fixtures green, every shipped HTML `0 P0 · 0 P1`.
CI enforces the same on `main`.

## Conventions

- One self-contained file per artifact; tokens in `:root` only; no new runtime dependencies.
- Placeholders stay labeled (`[REPLACE · label]`) — never invent metrics, tools, or costs.
- Changelog: add every user-facing change under `CHANGELOG.md → [Unreleased]`.
- Releases are cut by pushing a `v*` tag; notes build automatically from the changelog.

## Security

Suspected vulnerabilities go through the private channel in `SECURITY.md` — never a public issue or PR.

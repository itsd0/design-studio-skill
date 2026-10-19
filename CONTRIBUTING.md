# Contributing

## What lands

- Design-system changes (`SKILL.md`, `references/`, `assets/`) with before/after rationale.
- Linter rules in `scripts/lint.py`, each with a fixture in `tests/fixtures/` and a case in `tests/run_tests.py`.
- Render-gate rules in `scripts/verify.py` (or `scripts/probe.js`), each with a render fixture and a case in `tests/run_tests.py`.
- Demo artifacts that pass `scripts/lint.py` **and** `scripts/verify.py` with zero P0/P1.

## Required checks (run before every PR)

```bash
python3 tests/run_tests.py
python3 scripts/lint.py index.html assets/*.html demo/*.html
python3 scripts/verify.py index.html assets/*.html demo/*.html
```

All must pass: fixtures green, every shipped HTML `0 P0 · 0 P1` from the source linter and from the render gate. The render gate needs Chrome/Chromium; without one it prints "skipped" and exits 0, so the check is still meaningful on a machine that has it.
CI enforces the same on `main`.

## Conventions

- One self-contained file per artifact; tokens in `:root` only; no new runtime dependencies.
- Placeholders stay labeled (`[REPLACE · label]`) — never invent metrics, tools, or costs.
- Changelog: add every user-facing change under `CHANGELOG.md → [Unreleased]`.
- Releases are cut by pushing a `v*` tag; notes build automatically from the changelog.
- Both `--json` contracts (`docs/lint-schema-v1.md`, `docs/verify-schema-v1.md`) are additive-only — never retype or remove a key.

## Security

Suspected vulnerabilities go through the private channel in `SECURITY.md` — never a public issue or PR.

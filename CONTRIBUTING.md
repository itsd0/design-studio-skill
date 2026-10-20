# Contributing

## What lands

- Design-system changes (`SKILL.md`, `references/`, `assets/`) with before/after rationale.
- Linter rules in `scripts/lint.py`, each with a fixture in `tests/fixtures/` and a case in `tests/run_tests.py`.
- Render-gate rules in `scripts/verify.py` (or `scripts/probe.js`), each with a render fixture and a case in `tests/run_tests.py`.
- Contract rules in `scripts/contract.py`, extract rules in `scripts/extract.py`, score rules in `scripts/score.py` — each with a case in `tests/run_tests.py`.
- Library entries in `references/library/`, complete and contrast-safe (`run_library` checks every one).
- Demo artifacts that pass all four gates with zero P0/P1 and a clean craft scorecard.
- Skill-file changes that keep `tests/test_skill_md.py` green: budget, sections, and every path it mentions must exist.

## Required checks (run before every PR)

```bash
python3 tests/run_tests.py
python3 scripts/lint.py index.html assets/*.html demo/*.html
python3 scripts/verify.py index.html assets/*.html demo/*.html
python3 scripts/contract.py demo/landing.html --design demo/design.md
python3 scripts/score.py index.html demo/*.html
python3 tests/test_skill_md.py
```

The skill file is gated too: name, description length and triggers, token and line budgets, required sections, and every path it mentions.

All must pass: fixtures green, every shipped HTML `0 P0 · 0 P1` from the source linter and the render gate, no contract drift, and no failed craft check. The render gate and the scorecard need Chrome/Chromium; without one they print "skipped" and exit 0, so the checks are still meaningful on a machine that has it.
CI enforces the same on `main`.

## The four gates

| Gate | Reads | Needs |
|---|---|---|
| `lint.py` | the source | nothing |
| `verify.py` | the rendered page | Chrome/Chromium |
| `contract.py` | the artifact and its `DESIGN.md` | nothing |
| `score.py` | the rendered page | Chrome/Chromium |

A rule only lands with a fixture, a test case, and a line in the reference it belongs to.

## Conventions

- One self-contained file per artifact; tokens in `:root` only; no new runtime dependencies.
- Placeholders stay labeled (`[REPLACE · label]`) — never invent metrics, tools, or costs.
- Changelog: add every user-facing change under `CHANGELOG.md → [Unreleased]`.
- Releases are cut by pushing a `v*` tag; notes build automatically from the changelog.
- Both `--json` contracts (`docs/lint-schema-v1.md`, `docs/verify-schema-v1.md`) are additive-only — never retype or remove a key.

## Security

Suspected vulnerabilities go through the private channel in `SECURITY.md` — never a public issue or PR.

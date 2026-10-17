# Changelog

All notable changes to Design Studio are documented here, newest first.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.4.0] — 2026-10-18

### Added
- Pinned installs: `install.sh` accepts `VERSION` (e.g. `VERSION=v1.4.0 … | sh`) and verifies the tarball against the per-release `SHA256SUMS` asset.
- `SECURITY.md`: supported-versions table and private-report channel.
- `docs/lint-schema-v1.md`: frozen `--json` finding shape (additive-only); enforced by a schema test in `tests/run_tests.py`.
- CI (`.github/workflows/ci.yml`): rule fixtures, shipped-artifact lint (zero P0/P1), and a GitHub Pages smoke check on every push and pull request.
- Release automation (`.github/workflows/release.yml`): pushing a `v*` tag builds the release notes from this changelog and uploads `SHA256SUMS`.

## [1.3.2] — 2026-10-17

### Fixed
- Mobile overflow at 390px: `minmax(0, 1fr)` collapse plus `min-width: 0` on grid children in every shipped file (verified `scrollWidth === clientWidth` at a real 390px viewport).
- Inspector activity meta stacks under each title — nothing clips at 1440px.
- Thread view moved after the eval receipt in `demo/agent.html`, so run-detail steps read in order.
- New P1 lint gate `mobile-grid-1fr` with fixture.

## [1.3.1] — 2026-10-17

### Added
- Run header with Stop/Cancel plus elapsed time, tokens, and cost (`[data-run]` + `[data-run-control="stop"]`).
- Named destructive approvals, danger-neutral treatment, numbered full-border plan steps, timeline done/current/pending states with connectors, muted success pills, Args + output preview on every active tool call, icon/timestamp activity feed, sticky mobile approval bar, thread view in `demo/agent.html`.
- Lint gates: `run-missing-stop` (P0), `destructive-approve-unnamed` (P0), `tool-call-missing-output` (P1), agent `accent-overuse` (P1).

### Fixed
- `missing.extend(f"…")` → `append` in `tests/run_tests.py`.

## [1.3.0] — 2026-10-17

### Added
- New `agent` artifact kind (`thread` / `run-detail` / `approval` / `activity`) with `references/agent-ux.md` contracts.
- `assets/agent-seed.html`, `assets/agent-ux-patterns.html`, and `demo/agent.html` (incident-triage demo).
- Lint gates: `tool-call-missing-status` (P0), `destructive-without-approval` (P0), `stream-missing-aria-live` (P1).

## [1.2.1] — 2026-10-16

### Fixed
- Direction count corrected to 8 in `SKILL.md`; `docs/ROADMAP.md` notes the v1.2.0 expansion.
- Flagship visual rules yield to an existing `DESIGN.md` (brand contract always wins).
- New P1 `dashboard-missing-craft` lint gate with fixture.

## [1.2.0] — 2026-10-16

### Added
- 8 curated visual directions (new dark-native `dark-structural-grid`, `neo-brutalist-terminal`, `atmospheric-craft-dark`) with `--accent-on` + `--surface-2`.
- Schematic primitives (`.bento-hairline`, `.app-window`, `.tone-muted`, `.index-showcase`), 11 section skeletons, visual-craft lint gate.
- Official landing page (`index.html`) served on GitHub Pages.

## [1.1.0] — 2026-10-16

### Added
- Linter v2 (computed WCAG contrast, accessibility statics, `--json`), four new references, dashboard/mobile/UI-pattern seeds, experience dials, self-tests, demo dashboard.

## [1.0.0] — 2026-10-16

### Added
- Initial public release: `DESIGN.md` brand contract, 5 visual directions, page/deck seeds, anti-slop linter, one-line installer.

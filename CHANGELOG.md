# Changelog

All notable changes to Design Studio are documented here, newest first.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.5.0] — 2026-10-19

### Added
- **Render gate** — `scripts/verify.py` loads an artifact in headless Chrome at 390px, 768px and 1440px and reports what source analysis cannot see: horizontal overflow (naming the element that causes it), text clipped by an `overflow: hidden` box (naming the culprit), computed text contrast for every text run, tap targets under 24×24 CSS px, runtime JavaScript errors, missing image dimensions, missing focus indicators, and a missing or zoom-blocking viewport meta.
- `scripts/probe.js` — the in-page probe the verifier injects. It parses `color(srgb …)`, `oklch()` and `color-mix()` results, composites alpha backgrounds, and applies the WCAG 2.2 inline and spacing exceptions for tap targets.
- `docs/verify-schema-v1.md` — frozen `--json` contract for the render gate (additive-only), pinned by a schema test.
- `tests/compose.py` — paste a fragment into a seed so the result can be rendered and verified; used by the new composition test.
- Render fixtures (`tests/fixtures/good-render.html`, `bad-render.html`) and a rendered-regression pass over every shipped artifact in `tests/run_tests.py`.
- CI job `render` — every shipped artifact plus the composed section library must render with zero P0/P1 findings.

### Fixed
- `index.html` scrolled sideways at 390px: the comparison table, the topnav button row and the app-window tab strip now constrain themselves.
- `demo/landing.html` clipped its app-window trace log at 390px.
- `assets/prototype-seed.html` and `demo/landing.html` app bars now wrap instead of clipping.
- Accent-coloured small text failed WCAG AA in the deck seed (3.7:1), the mobile seed (3.7:1) and the deck demo (3.8:1 / 4.3:1) — a darker `--accent-strong` weight now carries it, with a lighter one for dark surfaces.
- A white-on-accent primary button failed at 3.9:1 in `assets/ui-patterns.html` — the fill now uses `--accent-strong` with a bound `--accent-on`.
- Unstyled links in `assets/agent-ux-patterns.html` fell back to the browser's default blue on a dark surface (2.1:1).
- Controls under the 24×24 tap target: search inputs, nav links, standalone "View all" links, link-buttons and text fields in the seeds and demos.

### Changed
- `references/quality-gates.md` documents the two gates side by side; the delivery checklist now requires both.
- `SKILL.md` step 5 and the review mode run the render gate alongside the linter.
- CI pages-smoke retries the live probe instead of sleeping a fixed 90 seconds.

## [1.4.1] — 2026-10-18

### Added
- Governance: `CONTRIBUTING.md`, issue/PR templates, Code of Conduct, `docs/adopting.md` (pinning, air-gapped use, no telemetry).

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

# Design Studio

**A design skill for coding agents.** Hand it a brief; get back a polished, self-contained HTML artifact — a landing page, app prototype, dashboard, or slide deck — that opens in any browser with no build step and no runtime dependencies.

[![License: MIT](https://img.shields.io/badge/license-MIT-black.svg)](LICENSE)
[![CI](https://github.com/itsd0/design-studio-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/itsd0/design-studio-skill/actions/workflows/ci.yml)

**Live Landing Page:** [itsd0.github.io/design-studio-skill](https://itsd0.github.io/design-studio-skill/) · **Demos:** [Landing](https://itsd0.github.io/design-studio-skill/demo/landing.html) · [Dashboard](https://itsd0.github.io/design-studio-skill/demo/dashboard.html) · [Agent run](https://itsd0.github.io/design-studio-skill/demo/agent.html) · [Slide Deck](https://itsd0.github.io/design-studio-skill/demo/deck.html)

![Design Studio — flagship landing page built with the skill](docs/landing-hero.png)

The method, in one line: capture the brief → extract or derive a brand into a `DESIGN.md` contract → compare candidate directions, rendered side by side → plan before pixels → build from an architectural seed → pass four gates (source, render, contract, craft) → deliver one `index.html` you can open, ship, print to PDF, or screenshot.

## Install

Design Studio is a standard [Agent Skills](https://agentskills.io) skill — one install works for OpenCode, Claude Code, Codex, Cursor, and many more agents.

**Agent Skills installer (any supported agent):**

```bash
npx skills add itsd0/design-studio-skill -g
```

**Pinned, verified (recommended for teams):**

```bash
curl -fsSL https://raw.githubusercontent.com/itsd0/design-studio-skill/main/install.sh | VERSION=v1.8.0 sh
```

Pinned installs verify the tarball against the release's `SHA256SUMS`. See [`SECURITY.md`](SECURITY.md) and [`CHANGELOG.md`](CHANGELOG.md).

**OpenCode — plain git:**

```bash
git clone --depth 1 https://github.com/itsd0/design-studio-skill ~/.config/opencode/skills/design-studio
```

**No git, no node (macOS / Linux / WSL):**

```bash
curl -fsSL https://raw.githubusercontent.com/itsd0/design-studio-skill/main/install.sh | sh
```

**Windows (PowerShell):**

```powershell
git clone --depth 1 https://github.com/itsd0/design-studio-skill "$env:USERPROFILE\.config\opencode\skills\design-studio"
```

Restart your agent afterwards. `install.sh` honors `SKILLS_DIR` and `XDG_CONFIG_HOME` if your skills live elsewhere.

### The tools on their own

The gates and the instrument work without the skill — useful in CI, and in any agent that speaks MCP.

```bash
npx design-studio doctor          # check this machine
npx design-studio lint index.html # source gates
npx design-studio verify index.html
```

| Platform | Install |
|---|---|
| Any MCP agent | `claude mcp add design-studio -- python3 scripts/mcp_server.py` |
| Claude Code | `/plugin marketplace add itsd0/design-studio-skill` |
| Codex | `codex plugin marketplace add itsd0/design-studio-skill` |
| Cursor | copy `.cursor-plugin/` into the project's plugin directory |
| Gemini CLI | `gemini extensions install https://github.com/itsd0/design-studio-skill` |
| MCP registry | `server.json` — `npx design-studio-skill --stdio` |

The MCP server exposes eight tools: `design_studio_lint`, `design_studio_verify`, `design_studio_contract`, `design_studio_extract`, `design_studio_score`, `design_studio_directions`, `design_studio_handoff`, `design_studio_review`.

## Use it

Just ask:

- "Design a landing page for a local-first file transfer tool."
- "Prototype a dashboard for a homelab."
- "Design an approval screen for an incident-triage agent."
- "Build a six-slide pitch deck as a single HTML file."
- "Review this index.html against the quality gates and fix what fails."

The agent writes a real `index.html`, runs the linter **and** the render gate, and iterates until both pass.

## Demo

Three artifacts built from one brief, each a single self-contained file — [`demo/landing.html`](demo/landing.html), [`demo/dashboard.html`](demo/dashboard.html), and [`demo/deck.html`](demo/deck.html) — plus an agent run-detail demo, [`demo/agent.html`](demo/agent.html), and the brand contract they were built from, [`demo/design.md`](demo/design.md):

![The demo dashboard — Ferry transfers](docs/dashboard.png)

![The demo agent run — incident triage with plan approval](docs/agent.png)

![The demo landing page, full length](docs/landing-full.png)

<p>
  <img src="docs/deck-cover.png" width="49%" alt="Deck cover slide" />
  <img src="docs/deck-dark.png" width="49%" alt="Deck dark statement slide" />
</p>

The deck is keyboard, wheel, and touch navigable — counter, progress bar, dots, print-to-PDF styles, and a self-contained navigation runtime included. All three demo files pass the linter with zero findings.

## What's new in v1.8.0 (the skill file, the handoff, and the evidence)

- **`SKILL.md` rewritten to the Agent Skills authoring rules** — a Quick start, a workflow checklist, **ten Gotchas** from this repository's own releases, and **load triggers** instead of a resource-map menu. 3,896 → ~2,950 tokens.
- **The skill file is gated** — `tests/test_skill_md.py` checks the name, the description's triggers and boundary, the token and line budgets, the required sections, and that **every path it mentions exists**.
- **Handoff** — `design-studio handoff index.html` writes `HANDOFF.md`: tokens, type, page inventory, components, states, breakpoints, the accessibility contract and the acceptance checks. This is how a single-file artifact becomes work inside a framework.
- **Review** — `design-studio review index.html` writes a publishable review: verdict, findings per gate, scorecard, screenshots, and the judgement checklist that still needs a human.
- **Copy is now checked** — `references/copy.md` plus two scorecard rules: no generic errors, no vague buttons.
- **The design DNA library grew 6 → 18** — Swiss Poster, Bauhaus Primary, Japanese Minimal, Desert Warm, Noir Luxe, Terminal Green, Civic Blue, Pastel Playful, Neon Cyber, Monochrome Print, Arctic Precision, Trading Desk.
- **Compatibility is published, with dates** — [`docs/compatibility.md`](docs/compatibility.md): OpenCode ✅ connected (tools loaded in-session), Claude Code ✅ resolved, Gemini ✅ connected, Codex ✅ registered, Cursor ⚠️ manifest only.

## What's new in v1.7.0 (the full toolchain)

The v1.5.0 render gate proved a page can be clean in a diff and broken on screen. v1.7.0 closes the rest of the loop: from a brand URL to a verified artifact, with the decisions visible.

- **Contract fidelity** — `scripts/contract.py` diffs the artifact's `:root` against `DESIGN.md`: token drift and missing tokens are P0, font drift and unrecorded dials are P1. "DESIGN.md is the contract" is now mechanical, not a habit.
- **Design-system extractor** — `scripts/extract.py` turns a live URL, an HTML file or a reference screenshot into `DESIGN.md` + `tokens.css`, measuring the *rendered* page (including `color-mix()` results) and inferring the roles. The step that used to ask an agent to sample tokens by eye now has an instrument.
- **Direction studio** — `scripts/directions.py` derives three candidate directions from the brief and renders them side by side into one comparison sheet. The agent no longer picks a direction blind, and a fixed list of eight stops being the house style.
- **Craft scorecard** — `scripts/score.py` grades a rendered artifact against a review (hierarchy, type discipline, accent budget, section rhythm, states, self-containment) and reports **distance from the default look** — headline font, body font, accent family, background family. 2/4 is the floor.
- **The critique** — `references/critique.md` is the judgement layer: claim → hierarchy → accent → surface → evidence → states → rhythm → distance → handoff, with before/after examples for each.
- **Design DNA library** — `references/library/` holds eighteen offline, MIT design grammars with tokens, component recipes and anti-patterns.
- **Distribution** — an MCP server (eight tools, any MCP agent), one CLI (`design-studio <command>`), an npm bin, and plugin manifests for Claude Code, Codex, Cursor and Gemini.
- **Gallery and benchmarks** — `gallery/` publishes artifacts with their contract, and `scripts/benchmark.py` publishes one brief rendered three ways so the method's decisions are visible.

**The shipped artifacts got better too.** The scorecard measured our own pages at 2/4 from the default look — the display face was the system sans, which is exactly what every agent reaches for. They now lead with a serif (`ui-serif`, available on every platform without a webfont) and score 3/4.

## What's new in v1.5.0 (render gate)

The linter reads **source**. The verifier reads the **rendered page** — it loads the artifact in headless Chrome and measures what a human actually sees. It closes the gap between "the linter is clean" and "the page works".

- **New `scripts/verify.py`** — renders at 390px, 768px and 1440px and reports horizontal overflow (with the element that causes it), text clipped by an `overflow: hidden` box, **computed** text contrast (4.5:1 / 3:1 for large text), tap targets under 24×24, runtime JavaScript errors, missing image dimensions, missing focus indicators and a missing viewport meta. `--json` speaks a frozen shape ([`docs/verify-schema-v1.md`](docs/verify-schema-v1.md)); `--screenshot DIR` writes one PNG per viewport.
- **No new dependencies** — stdlib Python plus a Chrome/Chromium binary that already exists on most machines. Without one, the gate says so and exits 0.
- **New tests** — render fixtures, a rendered-regression pass over every shipped artifact, and a composition test that pastes the section library into the prototype seed and renders the result.
- **Real defects fixed in the shipped files** — the landing page scrolled sideways at 390px (comparison table, topnav row, app-window tabs), the app-window clipped its trace log, accent-coloured small text failed AA in the deck and mobile seeds (3.7:1), a white-on-accent button failed at 3.9:1, and several controls were under the 24×24 tap target.

## What's new in v1.4.1 (governance)

- `CONTRIBUTING.md`, issue and PR templates, Code of Conduct, and `docs/adopting.md` (pinning, air-gapped use, no-telemetry audit surface).

## What's new in v1.4.0 (enterprise-ready)

- **Pinned, verified installs** — `install.sh` accepts `VERSION=v1.4.0 … | sh` and checks the tarball against the release's `SHA256SUMS`.
- **`SECURITY.md`** — supported versions and a private-report channel.
- **Frozen `lint --json` contract** (`docs/lint-schema-v1.md`, additive-only), enforced by a schema test.
- **CI** — rule fixtures, shipped-artifact lint (zero P0/P1), and a GitHub Pages smoke check on every push and pull request; plus release automation that builds the notes from the changelog.

## What's new in v1.3.2 (Agent-UX hotfix)

- **No mobile overflow** — `minmax(0, 1fr)` collapse plus `min-width: 0` on grid children everywhere; long identifiers wrap on mobile. New P1 `mobile-grid-1fr` lint gate with fixture.
- **Readable inspector** — activity meta stacks under each title, so status, timestamp, and "View logs" never clip at 1440px.
- **Ordered run detail** — Thread view moved after the eval receipt, so approval precedes the conversation recap.

## What's new in v1.3.1 (Agent-UX quality pass)

- **Run controls** — every run view carries Stop/Cancel plus elapsed time, tokens, and cost (`[data-run]` + `[data-run-control="stop"]`; P0 `run-missing-stop`).
- **Named destructive approvals** — the approve button names its target (`Approve & restart checkout-api-02`), uses a neutral danger-tinted treatment instead of green, and keeps Reject equally weighted (P0 `destructive-approve-unnamed`).
- **Timeline states** — done `✓` muted, current accent + `aria-current="step"`, pending muted, connector lines, horizontal-scroll on mobile.
- **Craft details** — muted success pills (accent ≤ 2 uses; P1 `accent-overuse`), Args + output preview on every active tool call (P1 `tool-call-missing-output`), numbered full-border plan steps, icon + timestamp activity feed, sticky mobile approval bar, wider 1440px columns, thread view in `demo/agent.html`.

## What's new in v1.3.0 (Agent-UX artifact kind)

- **New `agent` artifact kind** — `thread`, `run-detail`, `approval`, `activity` screens for AI-agent products (`SKILL.md` Brief/Plan/Build + `references/agent-ux.md` contracts).
- **Agent seeds & patterns** — `assets/agent-seed.html` (runs sidebar + thread pane + inspector, 920px breakpoint) and `assets/agent-ux-patterns.html` (tool-call card, streaming, plan approval, guardrails, activity feed, run DAG, eval receipt, all states).
- **Agent lint gates** — `scripts/lint.py` enforces `tool-call-missing-status` (P0), `destructive-without-approval` (P0), and `stream-missing-aria-live` (P1) on pages with `data-artifact="agent"`.
- **Live demo** — [`demo/agent.html`](demo/agent.html): incident-triage run with step timeline, tool calls, guardrail, plan approval, and activity feed.

## What's new in v1.2.0 (2025–2026 Flagship Architecture)

- **8 curated flagship directions** — added dark-native engineering presets (`dark-structural-grid`, `neo-brutalist-terminal`, `atmospheric-craft-dark`) with obsidian canvases, exposed `1px` hairline grids, dual-tone headlines (`.tone-muted`, `.tone-block`), and `--accent-on` button ink safety.
- **High-craft schematic primitives** — `.bento-hairline` (gapless `1px` cells), `.bento-visual` (inline SVG latency gauges, isometric volume cubes, `FORK → BUILD → EVAL` DAG trees, wireframe globes), `.app-window` (multi-pane studio/runtime workspace), and `.index-showcase` (numbered `01`–`04` tab matrices).
- **Visual craft lint gate** — `scripts/lint.py` now enforces `missing-visual-craft` on multi-section landing pages and evaluates inline SVG schematics as unified accent moments.

## What's new in v1.1.0

- **Linter v2** — computed WCAG contrast for the core token pairs, static accessibility checks (`lang`, `alt`, control labels, zoom, focus, heading structure), and `--json` output. New self-tests in `tests/` keep the shipped seeds and demos clean.
- **Four new references** — [`motion.md`](references/motion.md) (durations, easing, reduced-motion), [`ux-flows.md`](references/ux-flows.md) (loading / empty / error states, microcopy), [`data-viz.md`](references/data-viz.md) (chart craft), [`ui-patterns.md`](references/ui-patterns.md) (component contracts).
- **Three new seeds** — `dashboard-seed.html` (rail, KPI row, SVG chart, table), `mobile-seed.html` (device frame), and `ui-patterns.html` (paste-ready component states); the section library grew to 11 blocks with schematic bentos, pricing, and prose.
- **Workflow upgrades** — experience dials (density / expressiveness / motion) captured at brief time, a review mode for audits, and a verify-with-screenshot step.

## What's inside

| Path | Purpose |
|---|---|
| `index.html` | Official Design Studio flagship landing page (live on GitHub Pages) |
| `SKILL.md` | The workflow the agent follows + non-negotiables |
| `references/design-md.md` | Brand contract: section order, standard token names, experience dials |
| `references/directions.md` | 8 curated visual directions (2025–2026 flagship dark + light palettes, fonts) |
| `references/artifact-contract.md` | Output rules: layout, imagery, dark mode, dashboards, mobile, exports |
| `references/deck-contract.md` | Deck mode: slide themes, rhythm, navigation runtime |
| `references/quality-gates.md` | Anti-slop + craft rules, WCAG 2.2 checklist, P0/P1/P2 gates |
| `references/motion.md` | Durations, easing curves, choreography, reduced-motion recipes |
| `references/ux-flows.md` | Loading / empty / error states, microcopy, navigation models |
| `references/data-viz.md` | Chart selection, axis and label craft, inline-SVG conventions |
| `references/ui-patterns.md` | Overlay ladder, component contracts, state machine |
| `references/agent-ux.md` | Agent screens: tool-call card, streaming, plan approval, guardrails, activity feed, run DAG, eval receipt |
| `assets/design-md.template.md` | Starter brand contract |
| `assets/prototype-seed.html` | Page/app seed: tokens + hairline bento + studio window + pricing/prose blocks |
| `assets/dashboard-seed.html` | Dashboard seed: rail, topbar, hairline KPI row, SVG chart, table |
| `assets/mobile-seed.html` | Mobile seed: device frame, status bar, tab bar |
| `assets/agent-seed.html` | Agent seed: runs sidebar, thread/run pane, inspector |
| `assets/agent-ux-patterns.html` | Paste-ready agent patterns (tool call → eval receipt) |
| `assets/ui-patterns.html` | Paste-ready component states (buttons → table toolbar) |
| `assets/section-skeletons.html` | 11 paste-ready sections (hero-stage, schematic bentos, indexed showcase, pricing, CTA…) |
| `assets/deck-seed.html` | Deck seed: themes, chrome, nav runtime, print CSS |
| `scripts/lint.py` | Anti-slop + a11y + contrast linter (fails on P0, advises on P1/P2) |
| `scripts/verify.py` | Render gate — loads the artifact in headless Chrome and reports overflow, clipping, computed contrast, tap targets, runtime errors |
| `scripts/contract.py` | Contract fidelity — diffs the artifact's `:root` against `DESIGN.md` |
| `scripts/extract.py` | Design-system extractor — URL / file / screenshot → `DESIGN.md` + `tokens.css` |
| `scripts/score.py` | Craft scorecard + distance from the default look |
| `scripts/directions.py` | Candidate directions from a brief + a rendered comparison sheet |
| `scripts/benchmark.py` | Publishes a benchmark page: one brief, three directions, rendered |
| `scripts/mcp_server.py` | MCP server — the same eight tools in any MCP-capable agent |
| `scripts/handoff.py` | Implementation spec from an approved artifact |
| `scripts/review.py` | Publishable review document across all four gates |
| `scripts/ds.py` | One CLI for all of the above |
| `docs/lint-schema-v1.md` | Frozen `--json` contract (additive-only) for CI integrations |
| `docs/verify-schema-v1.md` | Frozen `--json` contract for the render gate |
| `references/critique.md` | The judgement layer — nine review steps with before/after examples |
| `references/copy.md` | Error, empty-state, CTA and onboarding copy rules |
| `docs/compatibility.md` | Verified platforms, dates, and what is *not* verified |
| `references/library/` | Eighteen offline design-DNA grammars with tokens, recipes and anti-patterns |
| `gallery/` | Published artifacts, their contracts, and the method's benchmarks |
| `tests/run_tests.py` | Self-tests: rule fixtures + shipped artifacts stay clean |
| `demo/` | Finished example artifacts + the DESIGN.md behind them |
| `install.sh` | One-line installer (`VERSION=` pin + `SHA256SUMS` verify) |
| `CHANGELOG.md` | Release history (Keep a Changelog) |
| `SECURITY.md` | Supported versions + private-report channel |
| `CONTRIBUTING.md` | Checks, conventions, changelog duty |
| `docs/adopting.md` | Pinning, air-gapped use, no-telemetry, review checklist |

## The linter

```bash
python3 scripts/lint.py index.html
```

Exit code `1` means at least one must-fix (P0) finding. Works on any single-file HTML artifact. It catches the standardized AI-slop tells — purple/indigo defaults, two-stop "trust" gradients, emoji iconography, left-accent cards, invented metrics, filler copy, broken deck themes — and now also:

- computes **WCAG contrast** for the core token pairs (foreground, muted, and accent against the surfaces) per theme and prints the ratios;
- checks the **accessibility statics**: `lang`, `alt`, control labels, zoom blockers, focus removal, heading structure;
- speaks `--json` for review reports:

```bash
python3 scripts/lint.py --json index.html
```

## The render gate

The linter reads source. The verifier reads the **rendered page**.

```bash
python3 scripts/verify.py index.html
```

It loads the artifact in headless Chrome at 390px, 768px and 1440px and reports what source analysis cannot see:

- **horizontal overflow** — the page scrolls sideways, and which element causes it;
- **clipped text** — content cut off by an `overflow: hidden` box, with the culprit element named;
- **computed contrast** — every text run measured against its real background, including `color-mix()` results (the token-level check only covers the declared pairs);
- **tap targets** — interactive controls under 24×24 CSS px, with the WCAG 2.2 inline and spacing exceptions applied;
- **runtime errors**, missing image dimensions, missing focus indicators, a missing viewport meta.

```bash
python3 scripts/verify.py --json index.html          # machine-readable
python3 scripts/verify.py --screenshot .shots index.html   # one PNG per viewport
```

Exit code `1` means at least one P0. Needs a Chrome/Chromium binary — without one it reports "skipped" and exits 0, so it never blocks an offline install. The frozen output shape lives in [`docs/verify-schema-v1.md`](docs/verify-schema-v1.md).

## Quality gates, in one breath

One token block; one accent with a hard budget; a display face bound to the direction, never the default; measured contrast instead of vibes; loading, empty, and error states on anything stateful; no `scrollIntoView`; a 920px reflow that actually works; decks that alternate light/dark with a nav runtime that respects iframes. The full checklist — including the WCAG 2.2 AA pass — lives in [`references/quality-gates.md`](references/quality-gates.md).

## The four gates

| Gate | Reads | Needs | Catches |
|---|---|---|---|
| `lint.py` | the source | nothing | slop, raw hex, token names, structure, static a11y |
| `verify.py` | the rendered page | Chrome/Chromium | horizontal overflow, clipped text, computed contrast, tap targets, runtime errors |
| `contract.py` | the artifact and its `DESIGN.md` | nothing | brand drift — a token that no longer matches the contract |
| `score.py` | the rendered page | Chrome/Chromium | hierarchy, type discipline, accent budget, rhythm, distance from the default look |

Run all four. A file can pass the linter and still scroll sideways at 390px; a file can pass every gate and still be the same page every agent produces. The first pair is correctness, the second pair is taste.

## Requirements

- Python 3.9+ — for the gates and the tools
- Chrome or Chromium — for the render gate and the scorecard only (optional; the skill works without it)
- The artifacts themselves are plain HTML/CSS/JS: no dependencies, no build step

## Credits

Portions of this skill — the artifact linter, the deck runtime, and parts of the design method — are adapted from the [open-design](https://github.com/nexu-io/open-design) project, licensed under the Apache License 2.0.

## License

[MIT](LICENSE)

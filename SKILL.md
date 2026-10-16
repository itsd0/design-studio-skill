---
name: design-studio
description: Build polished single-file HTML design artifacts — landing pages, web/app prototypes, dashboards, and slide decks — driven by a DESIGN.md brand contract, with anti-AI-slop quality gates, computed WCAG contrast, and a self-lint script. Use when the user wants to design or prototype a page, UI, dashboard, or presentation/deck as HTML; turn a brief into a polished visual artifact; establish or apply a brand/design system; or review and refine an existing HTML artifact.
license: MIT
---

# Design Studio

Turn a brief into **single-file HTML artifacts** driven by a **DESIGN.md brand contract**, passing **anti-slop craft gates**, delivered as real, handoff-ready files.

## Non-negotiables

1. **One self-contained file.** `index.html` — all CSS in a single `<style>` block, no external CSS/JS, inline SVG for charts, system-first fonts. Real images are copied into the project and referenced relatively.
2. **One token block.** Palette and type live in a single `:root` with standard names (`--bg`, `--surface`, `--surface-2`, `--fg`, `--muted`, `--border`, `--accent`, `--accent-on`, `--font-display`, `--font-body`, `--font-mono`). No raw hex outside it; derive tones with `color-mix()`.
3. **DESIGN.md is the brand contract.** Read it before writing HTML. Never invent tokens — if a value is missing, use the closest existing token.
4. **2025–2026 Flagship Visual Architecture.** Never ship a bare text-only hero or "3 small icons over paragraphs" feature sections. Every product/landing page must include a **Hero Product Stage** (`.app-window` multi-pane studio/IDE frame, `.term` session, or live telemetry schematic) and **Schematic Bento / Indexed Feature Sections** (`.bento-hairline` with `.bento-visual` SVG diagrams: gauges, isometric layers, `FORK → BUILD → EVAL` DAG pipelines, wireframe globes, and `.index-showcase` `01`–`04` tabs).
5. **Accent budget: at most 2 visible uses per screen.** Links demote to `--fg` when a CTA shares the screen. Always bind `--accent-on` so primary buttons have crisp WCAG contrast.
6. **No AI-slop tropes**: no purple/indigo defaults, no two-stop "trust" gradients, no emoji-as-icons, no rounded card with a colored left border, no invented metrics, no filler copy. Full list in `references/quality-gates.md`.
7. **Anchor every section.** `data-design-id="kebab-slug"` on each top-level `<section>`; decks use `data-screen-label="01 Cover"`.
8. **No `scrollIntoView()`** anywhere — it breaks embed and preview iframes.
9. **Self-check before delivery.** Run `python3 scripts/lint.py <file>` until zero P0 findings — fix every contrast `✗` — then walk the P0/P1 checklist in `references/quality-gates.md`.
10. **Deliver with a one-line summary** naming the file. Never paste the full HTML into chat.

## Workflow

### 0 · Preflight

- Read `references/artifact-contract.md` (always) and `references/deck-contract.md` when the artifact is a deck. Skim `references/quality-gates.md` once.
- Look for `DESIGN.md` (and `tokens.css`) in the working directory. If found, read both before writing anything.

### 1 · Brief

Capture: product, audience, goal, artifact kind (landing / prototype / dashboard / deck / mobile), must-keep facts (real numbers, names, copy) — **and the three experience dials**: density (airy · regular · compact), expressiveness (restrained · assured · bold), motion (still · standard · lively). Ask **only** for missing essentials, in one round. Facts you cannot know become labeled placeholders (`[REPLACE · label]`) — never invent statistics or quotes.

### 2 · Direction & design system

- **Brand exists** (URL, screenshot, brand assets): sample the core tokens (`--bg`, `--surface`, `--surface-2`, `--fg`, `--muted`, `--border`, `--accent`, `--accent-on`) and write or update `DESIGN.md` per `references/design-md.md` — including the dials. Start from `assets/design-md.template.md`.
- **No brand**: pick ONE direction from `references/directions.md` (`dark-structural-grid` · `neo-brutalist-terminal` · `atmospheric-craft-dark` · `editorial-monocle` · `modern-minimal` · `human-approachable` · `tech-utility` · `brutalist-experimental`). For AI infrastructure, developer tools, agent runtimes, and technical SaaS, default to one of the dark-native flagship directions (`dark-structural-grid`, `neo-brutalist-terminal`, or `atmospheric-craft-dark`) unless light mode is requested. State the direction and its accent in one sentence.
- Bind palette and fonts **verbatim** — never improvise hex values from a direction's label.

### 3 · Plan before pixels

- **Landing / prototype**: choose 4–6 sections with flagship visual rhythm (`hero-stage` with `.app-window` studio/runtime preview → `bento-telemetry` gapless hairline schematics → `bento-architecture` *or* `indexed-showcase` `01`–`04` tab matrix → `compare` hairline table *or* `pricing` → `cta`). State the section list to the user before writing HTML.
- **Deck**: pick the slide count by format (5–10 min talk ≈ 6 slides; 15 min ≈ 8–10; 20–30 min ≈ 12–18) and sketch the theme rhythm — `01 hero light · 02 light · 03 hero dark …`. No 3+ same-theme slides in a row; for 8+ slides include at least one `hero dark` and one `hero light`.
- **Dashboard**: classify the monitored domain, then define specific KPI names and plausible values — no "Metric A / Metric B".
- **Mobile**: one screen = one job. Pick the screen (feed, detail, onboarding, profile, checkout) and the single decision it supports.

### 4 · Build

- Start from the seed for the artifact kind: `assets/prototype-seed.html` (pages), `assets/dashboard-seed.html`, `assets/mobile-seed.html`, `assets/deck-seed.html` — copy it to `index.html` (or the slug the user expects).
- For app/UI states beyond the seeds, paste from `assets/ui-patterns.html` (buttons, fields, modal, toast, empty, skeleton, tabs, menu, table toolbar); paste page sections from `assets/section-skeletons.html` (`hero-stage`, `bento-telemetry`, `bento-architecture`, `indexed-showcase`, `compare`, `pricing`, `cta`). Customize every `.bento-visual` SVG schematic, `.app-window` pane, and `.dag-grid` to match the brief's exact domain — zero filler.
- Imagery: use real assets when obtainable (fetch the correct real image, copy it into the project, set intrinsic `width`/`height` on `<img class="content-img">`). Otherwise keep an **intentionally labeled** placeholder and disclose the limitation. Never hotlink; never invent a stand-in for a real person, product, or landmark.
- Motion follows `references/motion.md`: transform/opacity only, exits faster than enters, and any artifact that animates ships the reduced-motion path.
- Stateful and data surfaces cover the five states per `references/ux-flows.md`; charts follow `references/data-viz.md`.
- Keep the seeds' responsive breakpoints (920px) and, for decks, the navigation script intact.

### 5 · Self-check & lint

1. Run `python3 scripts/lint.py index.html` → fix every P0; read the contrast line and fix any `✗` pair (treat `(large/UI only)` pairs as fills and display text).
2. Walk the P0 checklist in `references/quality-gates.md`.
3. Spot-check: no raw hex outside `:root`; accent visible ≤ 2× on the rendered screen; reflow at ≤ 920px; for decks `grep 'class="slide' index.html` reads as a healthy rhythm.
4. Render and screenshot the file (any headless Chrome: `chrome --headless --screenshot=out.png --window-size=1440,900 index.html`) and apply the soul test to the image.

### 6 · Deliver & iterate

- One short summary: file name plus what it contains. Nothing after.
- Handoff note: the artifact is real HTML/CSS — drop it into a repository, open it in a browser, print to PDF, or screenshot for review.
- Revisions: apply surgical edits to the same file (do not regenerate wholesale), re-run the linter, and keep the copy specific to the brief.

### 7 · Review mode (audit requests)

When the user asks to review or audit an existing artifact rather than build one:

1. Run the linter — human output for reading, `python3 scripts/lint.py --json <file>` for pasting into a report.
2. Walk `references/quality-gates.md` top to bottom against the file — rhythm and state coverage, not just mechanics.
3. Report findings as a table — severity · id · where · fix — P0 first, before touching anything.
4. Fix with surgical edits (never regenerate), re-run the linter, and show the before/after contrast line when it changed.

## Resource map

| Path | Use |
|---|---|
| `references/design-md.md` | DESIGN.md contract, standard token names, experience dials, brand authoring |
| `references/directions.md` | 5 curated visual directions with palettes and fonts |
| `references/artifact-contract.md` | Output rules: layout, imagery, dark mode, dashboards, mobile, exports |
| `references/deck-contract.md` | Deck mode: slides, theme rhythm, navigation runtime |
| `references/quality-gates.md` | Anti-slop + craft rules, WCAG checklist, P0/P1/P2 gates, review protocol |
| `references/motion.md` | Durations, easing curves, choreography, reduced-motion recipes |
| `references/ux-flows.md` | Five data states, empty/error/loading formulas, microcopy, navigation models |
| `references/data-viz.md` | Chart selection, axis/label craft, KPI formula, inline-SVG conventions |
| `references/ui-patterns.md` | Overlay ladder, component contracts, the state machine |
| `assets/design-md.template.md` | Starter brand contract |
| `assets/prototype-seed.html` | Page/app seed: tokens, class system, pricing + prose blocks |
| `assets/dashboard-seed.html` | Dashboard seed: rail, topbar, KPI row, SVG chart, table |
| `assets/mobile-seed.html` | Mobile seed: device frame, status bar, tab bar |
| `assets/ui-patterns.html` | Paste-ready component states (buttons through table toolbar) |
| `assets/section-skeletons.html` | 10 paste-ready sections (hero → pricing → prose) |
| `assets/deck-seed.html` | Deck seed (visual system + navigation runtime) |
| `scripts/lint.py` | Anti-slop + a11y + contrast linter — run it before any delivery |
| `tests/run_tests.py` | Self-tests: rule fixtures + shipped artifacts stay clean |

Paths are relative to this skill's directory.

## When not to use

- Multi-page apps with routing, backend logic, or build tooling — this produces single-file artifacts, not codebases. Keep it as the design step, then hand off to a framework.
- Formal accessibility certification — the gates here are a professional baseline, not an audit.

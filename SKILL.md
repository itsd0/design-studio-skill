---
name: Design Studio
description: Build polished single-file HTML design artifacts — landing pages, web/app prototypes, dashboards, and slide decks — driven by a DESIGN.md brand contract, with anti-AI-slop quality gates and a self-lint script. Use when the user wants to design or prototype a page, UI, dashboard, or presentation/deck as HTML; turn a brief into a polished visual artifact; establish or apply a brand/design system; or review and refine an existing HTML artifact.
---

# Design Studio

Turn a brief into **single-file HTML artifacts** driven by a **DESIGN.md brand contract**, passing **anti-slop craft gates**, delivered as real, handoff-ready files.

## Non-negotiables

1. **One self-contained file.** `index.html` — all CSS in a single `<style>` block, no external CSS/JS, inline SVG for charts, system-first fonts. Real images are copied into the project and referenced relatively.
2. **One token block.** Palette and type live in a single `:root` with standard names (`--bg`, `--surface`, `--fg`, `--muted`, `--border`, `--accent`, `--font-display`, `--font-body`, `--font-mono`). No raw hex outside it; derive tones with `color-mix()`.
3. **DESIGN.md is the brand contract.** Read it before writing HTML. Never invent tokens — if a value is missing, use the closest existing token.
4. **Accent budget: at most 2 visible uses per screen.** Links demote to `--fg` when a CTA shares the screen.
5. **No AI-slop tropes**: no purple/indigo defaults, no two-stop "trust" gradients, no emoji-as-icons, no rounded card with a colored left border, no invented metrics, no filler copy. Full list in `references/quality-gates.md`.
6. **Anchor every section.** `data-design-id="kebab-slug"` on each top-level `<section>`; decks use `data-screen-label="01 Cover"`.
7. **No `scrollIntoView()`** anywhere — it breaks embed and preview iframes.
8. **Self-check before delivery.** Run `scripts/lint.py <file>` until zero P0 findings, then walk the P0 checklist.
9. **Deliver with a one-line summary** naming the file. Never paste the full HTML into chat.

## Workflow

### 0 · Preflight

- Read `references/artifact-contract.md` (always) and `references/deck-contract.md` when the artifact is a deck. Skim `references/quality-gates.md` once.
- Look for `DESIGN.md` (and `tokens.css`) in the working directory. If found, read both before writing anything.

### 1 · Brief

Capture: product, audience, goal, artifact kind (landing / prototype / dashboard / deck / mobile), and must-keep facts (real numbers, names, copy). Ask **only** for missing essentials, in one round. Facts you cannot know become labeled placeholders (`[REPLACE · label]`) — never invent statistics or quotes.

### 2 · Direction & design system

- **Brand exists** (URL, screenshot, brand assets): sample the six seed tokens and write or update `DESIGN.md` per `references/design-md.md`. Start from `assets/design-md.template.md`.
- **No brand**: pick ONE direction from `references/directions.md` (editorial · modern minimal · human · tech utility · brutalist). State the direction and its accent in one sentence. Offer up to three options only if the user explicitly asks to compare.
- Bind palette and fonts **verbatim** — never improvise hex values from a direction's label.

### 3 · Plan before pixels

- **Landing / prototype**: choose 4–6 sections with alternating rhythm (hero → features → stat *or* quote → split detail → CTA). State the section list to the user before writing HTML.
- **Deck**: pick the slide count by format (5–10 min talk ≈ 6 slides; 15 min ≈ 8–10; 20–30 min ≈ 12–18) and sketch the theme rhythm — `01 hero light · 02 light · 03 hero dark …`. No 3+ same-theme slides in a row; for 8+ slides include at least one `hero dark` and one `hero light`.
- **Dashboard**: classify the monitored domain, then define specific KPI names and plausible values — no "Metric A / Metric B".

### 4 · Build

- Start from `assets/prototype-seed.html` or `assets/deck-seed.html`; copy it to `index.html` (or the slug the user expects).
- Swap the `:root` tokens; paste and adapt sections from `assets/section-skeletons.html`; replace every `[REPLACE]` with real, brief-derived copy — zero filler.
- Imagery: use real assets when obtainable (fetch the correct real image, copy it into the project, set intrinsic `width`/`height` on `<img class="content-img">`). Otherwise keep an **intentionally labeled** placeholder and disclose the limitation. Never hotlink; never invent a stand-in for a real person, product, or landmark.
- Keep the seeds' responsive breakpoints (920px) and, for decks, the navigation script intact.

### 5 · Self-check & lint

1. Run `python3 scripts/lint.py index.html` → fix every P0; address P1s.
2. Walk the P0 checklist in `references/quality-gates.md`.
3. Spot-check: no raw hex outside `:root`; accent visible ≤ 2× on the rendered screen; reflow at ≤ 920px; for decks `grep 'class="slide' index.html` reads as a healthy rhythm.

### 6 · Deliver & iterate

- One short summary: file name plus what it contains. Nothing after.
- Handoff note: the artifact is real HTML/CSS — drop it into a repository, open it in a browser, print to PDF, or screenshot for review.
- Revisions: apply surgical edits to the same file (do not regenerate wholesale), re-run the linter, and keep the copy specific to the brief.

## Resource map

| Path | Use |
|---|---|
| `references/design-md.md` | DESIGN.md contract, standard token names, how to author a brand |
| `references/directions.md` | 5 curated visual directions with palettes and fonts |
| `references/artifact-contract.md` | Output rules: layout, imagery, dashboards, mobile, exports |
| `references/deck-contract.md` | Deck mode: slides, theme rhythm, navigation runtime |
| `references/quality-gates.md` | Anti-slop and craft rules, P0/P1/P2 review checklist |
| `assets/design-md.template.md` | Starter brand contract |
| `assets/prototype-seed.html` | Desktop prototype seed (tokens + class system) |
| `assets/section-skeletons.html` | 8 paste-ready landing/prototype sections |
| `assets/deck-seed.html` | Deck seed (visual system + navigation runtime) |
| `scripts/lint.py` | Anti-slop linter — run it on every artifact before delivery |

Paths are relative to this skill's directory.

## When not to use

- Multi-page apps with routing, backend logic, or build tooling — this produces single-file artifacts, not codebases. Keep it as the design step, then hand off to a framework.
- Formal accessibility certification — the gates here are a professional baseline, not an audit.

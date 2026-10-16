# Artifact contract — how the output is shaped

Every artifact is **one self-contained HTML file** (`index.html` unless the project already names a slug). It reads the active DESIGN.md, binds one `:root` token block, and is handed off as a real file — not a chat blob.

## Document skeleton

- `<!doctype html>` → `<html lang="en">` → `<head>` (charset, viewport, `<title>`) → one `<style>` block → `<body>` → optional single `<script>` block for behavior → `</html>`.
- All CSS inline in the single `<style>`. No `<link>` stylesheets, no external JS, no CDN imports. Google Fonts only when DESIGN.md explicitly names a face that cannot be system-stacked.
- Semantic structure: `<header>`, `<main>`, `<section>`, `<aside>`, `<footer>`.
- Charts and architectural schematics are hand-rolled inline SVG (`<polyline>`, `<path>`, `<polygon>`, `<rect>`, `<circle>`) — no chart libraries. Chart craft rules live in `references/data-viz.md`.
- `data-design-id="kebab-slug"` on every top-level `<section>` (comment-mode anchoring).

## Tokens

- One `:root` block carries the palette and type scale. Everything downstream references `var(--token)`; derived tones use `color-mix(in oklch, ...)`.
- Always bind the core eight tokens: `--bg`, `--surface`, `--surface-2`, `--fg`, `--muted`, `--border`, `--accent`, and `--accent-on` (contrast ink for text inside `--accent` buttons/badges).
- Never pure `#000` / `#fff` for page backgrounds — use the DESIGN.md or `references/directions.md` values (e.g., obsidian `oklch(13% 0.006 255)` for dark structural themes, `oklch(98% 0.004 95)` for light paper).
- Aim for zero raw hex outside `:root` (hard budget: ~12; a lint finding fires above that).

## Dark-first vs light-first themes

- **AI infrastructure, developer tools, agent runtimes, cloud platforms, and CLI/SDK products** default to a **dark-native flagship direction** (`dark-structural-grid`, `neo-brutalist-terminal`, or `atmospheric-craft-dark` in `references/directions.md`) unless the brief or `DESIGN.md` specifies light mode.
- When supporting both tiers, implement the secondary tier as a **token swap — never a second stylesheet** inside `@media (prefers-color-scheme: dark)` (or `light`).
- The linter computes contrast per theme scope — run it once and verify `fg/bg`, `fg/surface`, `muted/bg`, and `accent-on/accent`.

## Page composition (2025–2026 Flagship Landing / Prototype)

Default rhythms — pick one, then state the section list before writing HTML:

| Page kind | Flagship Rhythm |
|---|---|
| AI Infra / DevTool / SaaS Landing | `hero-stage` (Hero + multi-pane IDE/runtime window) → `bento-telemetry` (3-col gapless hairline schematic bento) → `bento-architecture` *or* `indexed-showcase` (`01`–`04` tab matrix) → `compare` (hairline matrix) → `cta` → `footer` |
| Product / Studio App | `hero-stage` (atmospheric hero + 3-pane studio canvas) → `indexed-showcase` → `bento-telemetry` → `pricing` → `cta` |
| Marketing / Editorial | `hero-split` → `log list` → `quote` → `compare` → `cta` |
| Pricing | `hero-center` → `pricing` (gapless hairline 3-tier matrix) → `compare` → `cta` |

### High-Craft Architecture Rules (Non-Negotiable):

1. **Hero Product Stage Required:** Never ship a bare text-only hero floating in empty space for a software product. Anchor the hero with a concrete product proof:
   - A multi-pane `.app-window` (left project tree, middle agent/prompt trace, right dot-matrix canvas preview), OR
   - A live `.term` CLI session / execution graph, OR
   - A high-precision SVG architectural schematic.
2. **Ban "3 Small Icons Over Paragraphs" Feature Sections:** Generic 3-column icon-plus-sentence grids read as low-effort AI templates. Instead, use:
   - **Gapless Hairline Bento (`.bento-hairline`):** Exposed `1px` structural grid (`gap: 1px; background: var(--border)`) where every `.bento-cell` includes a `.bento-visual` schematic (speed/latency arc gauge + `.cmd-pill`, isometric wireframe volume layers, DAG node pipeline `FORK → BUILD → EVAL`, or wireframe region globe), OR
   - **Numbered Index Showcase (`.index-showcase`):** Flush `01`–`04` monospace vertical tabs paired with a framed command-palette/agent-plan card and `.spec-list` engineering bullets.
3. **Dual-Tone & Block-Highlight Headlines:** Use lightness or block contrast inside `h1`/`h2` to create visual hierarchy:
   - Dual-tone: `<span class="tone-muted">Fast, Scalable, Stateful</span> Infrastructure for AI Agents.`
   - Block-highlight: `Give your AI secure access <mark class="tone-block">in minutes</mark>`
4. **Structural Chrome & Monospace Telemetry:** Use `var(--font-mono)` for numbered tabs (`01`), card titles (`.mono-title`), coordinates, latency badges, and command pills.
5. **Single Accent Budget (≤ 2 visible uses per screen):** Neutrals (`--bg`, `--surface`, `--surface-2`, `--border`, `--fg`, `--muted`) do 90% of the work; `--accent` is reserved for the primary CTA, active index indicator, and key telemetry signal stroke.
6. **Copy Discipline:** Headlines under 14 words; leads under two sentences (`max-width: 60ch`). Concrete engineering nouns and verifiable mechanisms — zero filler, zero invented metrics.

## Imagery & Schematics

- **Real referents get the real image.** For a named person, product, brand mark, cover, artwork, or landmark: fetch the correct real image, copy it into the project, reference it relatively.
- **Technical & product concepts get inline SVG/HTML schematics.** Build crisp monoline/isometric SVG diagrams (`stroke="var(--border)"` + signal highlights in `var(--accent)` and `var(--accent-soft)`) and realistic HTML/CSS micro-interfaces (`.app-window`, `.dag-grid`, `.cmd-pill`).
- No remote hotlinks, no placeholder CDNs (unsplash, placehold.co, picsum).

## Dashboards

Single-screen admin / observability / fleet console artifact — start from `assets/dashboard-seed.html` and keep the chart rules in `references/data-viz.md`:

- **Left sidebar** (220–260px): brand mark + version tag, 6–8 nav links with monoline icons, active state.
- **Top bar**: page title left; search + action button right. Sticky chrome, main scrolls independently.
- **Main**:
  - Row 1 — Gapless hairline KPI strip (`.kpis`): 3–4 KPI cells (monospace uppercase label, tabular-nums value, delta vs prior period in words).
  - Row 2 — Primary inline-SVG telemetry chart + secondary peer/node breakdown card.
  - Row 3 — Dense hairline data table with sort affordance, hover rows, status pills, and right-aligned monospace numeric columns.

## Mobile screens

- One screen = one job (feed, detail, onboarding, profile, checkout, or focus/hero).
- Render inside the device frame from `assets/mobile-seed.html` (status bar with inline-SVG icons, sensor cutout, home indicator, tab bar).
- Tap targets ≥ 44px; single accent ≤ 2 uses; numerics in mono; display in `var(--font-display)`.

## Responsive

- Break at 920px (seeds ship this): multi-column grids, `.bento-hairline`, `.app-panes`, and `.index-showcase` collapse cleanly to one column; no fixed widths.
- Verify mentally at 1440 / 768 / 375: no horizontal scroll, no clipped tables.

## Behavior & motion

- Static by default; interactions follow the choreography in `references/motion.md`.
- Any artifact that animates ships the `prefers-reduced-motion` kill switch.
- No `scrollIntoView()` anywhere. Use `scrollTo({ left, top, behavior })` on the actual scroller.
- Hover states on all links and buttons; `:focus-visible` ring on everything interactive.

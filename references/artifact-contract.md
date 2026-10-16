# Artifact contract — how the output is shaped

Every artifact is **one self-contained HTML file** (`index.html` unless the project already names a slug). It reads the active DESIGN.md, binds one `:root` token block, and is handed off as a real file — not a chat blob.

## Document skeleton

- `<!doctype html>` → `<html lang="en">` → `<head>` (charset, viewport, `<title>`) → one `<style>` block → `<body>` → optional single `<script>` block for behavior → `</html>`.
- All CSS inline in the single `<style>`. No `<link>` stylesheets, no external JS, no CDN imports. Google Fonts only when DESIGN.md explicitly names a face that cannot be system-stacked.
- Semantic structure: `<header>`, `<main>`, `<section>`, `<aside>`, `<footer>`.
- Charts are hand-rolled inline SVG (`<polyline>`, `<rect>`, `<circle>`) — no chart libraries.
- `data-design-id="kebab-slug"` on every top-level `<section>` (comment-mode anchoring).

## Tokens

- One `:root` block carries the palette and type scale. Everything downstream references `var(--token)`; derived tones use `color-mix(in oklch, ...)`.
- Never pure `#000` / `#fff` for surfaces — use the DESIGN.md values (fall back to `#0f0f0f` / `#fafafa`).
- Aim for zero raw hex outside `:root` (hard budget: ~12; a lint finding fires above that).

## Page composition (landing / prototype)

Default rhythms — pick one, then state the section list before writing HTML:

| Page kind | Rhythm |
|---|---|
| Landing | hero → 3 features → stat row *or* quote → split detail → CTA strip → footer |
| Marketing / editorial | hero-center → log list → split detail → CTA strip |
| Pricing | hero-center → comparison table → CTA strip |
| Docs index | hero-center → log list → CTA strip |

Rules:

- One hero, one CTA ask at the end. Alternate section types — two stat rows in a row, two quote blocks, or two feature triplets read as visual fatigue.
- Headlines under 14 words; leads under two sentences / ~60ch (`max-width: 60ch`).
- CTA labels say what happens: "Start free" beats "Get started"; "Read the story" beats "Learn more".
- At most one decorative flourish per page (a pull quote, a striking stat, one micro-interaction) — one, not three.
- Single accent, ≤ 2 visible uses per screen (default pair: eyebrow + primary CTA).
- Hero: 40–60vh typical for utility pages; generous but not full-screen unless the direction says so.
- Sections separated by whitespace first; borders/dividers only between unrelated top-level sections.

## Imagery

- **Real referents get the real image.** For a named person, product, brand mark, cover, artwork, landmark, or place: fetch the correct real image, copy it into the project, reference it relatively. Never generate, draw, or substitute a look-alike.
- **Illustrative / atmospheric subjects**: prefer real fetched photography; image generation is a fallback.
- Replace the seed's `.ph-img` scaffold with `<img class="content-img" width="[intrinsic w]" height="[intrinsic h]">` — keep the intrinsic ratio, full frame, no `object-fit: cover` on content images. Bounded on one axis for unusually tall/wide images.
- If no compliant asset can be acquired: keep an intentional, **labeled** placeholder (`.ph-img` with descriptive text) and disclose the limitation in the delivery summary.
- No remote hotlinks, no placeholder CDNs (unsplash, placehold.co, picsum). All images project-local.

## Dashboards

Single-screen admin / analytics artifact:

- **Left sidebar** (220–260px): brand mark, 6–8 nav links with icons, active state in the DS accent.
- **Top bar**: page title left; search + avatar/status right. Sidebar and top bar sticky; main scrolls independently (CSS grid shell).
- **Main**: row 1 — 3–4 KPI cards (label, one big number in mono tabular-nums, delta vs prior period); row 2 — primary inline-SVG chart; row 3 — secondary chart or table (recent events, top items).
- Real metric names and plausible values from the brief's domain — never "Metric A". Delta lines, not colored progress bars under numbers.
- Density follows the DESIGN.md mood — tight rows for trading/ops, airy for consumer.
- Accent budget still ≤ 2: typically sidebar active + one chart highlight.

## Mobile screens

- One screen = one job (feed, detail, onboarding, profile, checkout, or focus/hero). If the brief combines two, ship one and offer the other.
- Render inside a real-feeling device frame: status bar with inline-SVG icons, sensor cutout, home indicator. Keep the frame from the seed; don't re-implement it per screen.
- Tap targets ≥ 44px; single accent ≤ 2 uses; numerics in mono; display in `var(--font-display)`.

## Responsive

- Break at 920px (seeds ship this): multi-column grids collapse to one column; no fixed widths.
- Verify mentally at 1440 / 768 / 375: no horizontal scroll, no clipped tables (wrap tables in an overflow container).
- Fluid type via `clamp()` for display sizes; fixed px for UI text.

## Behavior & motion

- Static by default; if a micro-interaction is added, keep it 150–250ms, purposeful, and gate it behind `@media (prefers-reduced-motion: no-preference)`.
- No `scrollIntoView()` anywhere. Use `scrollTo({ left, top, behavior })` on the actual scroller.
- Hover states on all links and buttons; `:focus-visible` ring from `--focus-ring` or the seed's equivalent on everything interactive.

## Preview, export, handoff

- Preview: open the file in a browser, or serve locally (`python3 -m http.server`) when relative assets are involved.
- Exports: print-to-PDF works (include a clean print path for decks); HTML is the source of truth.
- Handoff: the artifact is real HTML/CSS — drop it into a codebase, port components to the stack, or use it as the visual spec. Mention the natural next step in one line.

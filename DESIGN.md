# Design Studio

> Category: Developer tooling / Design systems for coding agents
> The skill's own brand contract — the one its landing page is built from.

## Visual Theme & Atmosphere
Precision-engineered dark structural architecture (`dark-structural-grid`). Exposed
`1px` hairline grids, a serif display face over a grotesk body, dual-tone headlines
and a single phosphor green signal. Nothing floats on a blurry drop shadow — the
hairline grid carries the layout, and the accent is the only colour on screen.

## Experience Dials
- **Density:** `regular`
- **Expressiveness:** `assured`
- **Motion:** `still`

## Color Palette & Roles
- **Background (`--bg`):** `oklch(13% 0.006 255)` — the obsidian canvas
- **Surface (`--surface`):** `oklch(16% 0.008 255)` — panels, cells, IDE panes
- **Surface-2 (`--surface-2`):** `oklch(20% 0.010 255)` — active tabs, raised controls
- **Foreground (`--fg`):** `oklch(96% 0.004 255)` — primary headlines and UI copy
- **Muted (`--muted`):** `oklch(68% 0.012 255)` — secondary copy, captions
- **Border (`--border`):** `oklch(24% 0.010 255)` — the exposed `1px` structural hairline
- **Accent (`--accent`):** `oklch(80% 0.17 152)` — phosphor signal green: primary CTA, one hero element
- **Accent-On (`--accent-on`):** `oklch(15% 0.02 152)` — deep forest ink on an accent fill
- Anti-patterns: never a purple/indigo accent; never a gradient; never white text on a luminous accent; never a floating drop-shadow card where a hairline grid belongs.

## Typography Rules
- **Display / headings:** `ui-serif, 'Iowan Old Style', 'Charter', Georgia, 'Times New Roman', serif`, weight 600
- **Body:** `-apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Text', system-ui, sans-serif`, weight 400
- **Mono:** `'JetBrains Mono', 'Geist Mono', 'IBM Plex Mono', ui-monospace, Menlo, monospace`
- Scale (px): 12.5 · 15.5 · 18 · 20 · 30–46 · 44–72 (clamped)
- Line-height: 1.55 body, 1.04–1.08 display
- Letter-spacing: −0.028em on display sizes; +0.07em on uppercase mono labels
- Tabular numerics (`font-variant-numeric: tabular-nums`) wherever numbers align
- The display face is a **serif** on purpose: a system grotesk is the default every agent reaches for, and a skill used by everyone becomes the new default.

## Component Stylings
- **Buttons:** 6px radius, 9×16px padding; primary = `--accent` fill with `--accent-on` ink; secondary = transparent with a `1px` `--border`
- **Studio window (`.app-window`):** 3-pane hairline workspace with traffic lights, an active canvas tab and a dot-matrix inspection pane
- **Bento grid (`.bento-hairline`):** `gap: 1px; background: var(--border); border: 1px solid var(--border)`, flush cells, no radii on the cells
- **Tables:** a prose table cannot shrink below its longest word — every table sits in a `.tablewrap` scroller with `min-width: 0`, so the page never scrolls sideways

## Layout Principles
- Container 1180px, 32px gutters
- Sections separated by `1px solid var(--border)` hairlines, never by a colour change
- Desktop ≥ 921px: full multi-column hairline grids · Tablet/phone ≤ 920px: single-column collapse, `minmax(0, 1fr)`

## Depth & Elevation
- **Flat (0):** flush cells inside a hairline grid
- **Specular (1):** `inset 0 1px 0 color-mix(in oklch, var(--fg) 8%, transparent)` on `.app-window`, `.bento-visual` and `.card`
- No neumorphism, no glassmorphism, no drop shadows.

## Do's and Don'ts
- ✅ Anchor the hero with a multi-pane `.app-window` showing real workspace state
- ✅ One accent moment per screen, maximum two
- ✅ Let the hairline grid do the work
- ❌ Never ship a three-icon feature grid
- ❌ No emoji as icons — inline SVG only
- ❌ No invented metrics, no raw hex outside `:root`

## Responsive Behavior
- **Desktop ≥ 1024px:** 12-column grid, 1180px container
- **Tablet 640–1023px:** 8-column grid, 24px gutters
- **Phone < 640px:** 4-column grid; every grid collapses to `1fr`; tables scroll inside their own box; the topnav wraps

## Agent Prompt Guide
- Bind `:root` verbatim from this contract.
- Keep accent usage ≤ 2 visible moments per viewport.
- Every section carries `data-design-id`.
- When in doubt, subtract.
- If a request needs a colour that is not in this palette, use the closest token and surface a warning comment.

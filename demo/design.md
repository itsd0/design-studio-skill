# Ferry

> Category: AI Infrastructure / Local-First Peer Compute & File Fabric
> Sub-90ms peer-to-peer state, snapshot, and file streaming between developer machines and agent sandboxes.

## Visual Theme & Atmosphere
Precision-engineered dark structural architecture (`dark-structural-grid`). Exposed `1px` hairline bento grids, dual-tone headlines (crisp white + technical slate), multi-pane studio/runtime windows, and inline SVG telemetry schematics (latency gauges, isometric volume layers, concurrent DAG pipelines, and region globes). Nothing floats on blurry drop shadows; structural hairlines and top-edge specular highlights carry the layout.

## Experience Dials
- **Density:** `regular`
- **Expressiveness:** `assured`
- **Motion:** `standard`

## Color Palette & Roles
- **Background (`--bg`):** `oklch(13% 0.006 255)` — deep obsidian canvas
- **Surface (`--surface`):** `oklch(16% 0.008 255)` — bento cells, IDE panes, tables
- **Surface-2 (`--surface-2`):** `oklch(20% 0.010 255)` — active tabs, command pills, raised controls
- **Foreground (`--fg`):** `oklch(96% 0.004 255)` — primary headlines and UI copy
- **Muted (`--muted`):** `oklch(68% 0.012 255)` — secondary copy and dual-tone headline lead-ins
- **Border (`--border`):** `oklch(24% 0.010 255)` — exposed `1px` structural grid hairlines
- **Accent (`--accent`):** `oklch(80% 0.17 152)` — phosphor signal green (primary CTA, active index bar, telemetry signal stroke)
- **Accent-On (`--accent-on`):** `oklch(15% 0.02 152)` — deep forest ink for text inside `--accent` buttons and badges
- Anti-patterns: never use purple/indigo gradients; never put white text on luminous green buttons; never use floating drop-shadow cards where an exposed `1px` hairline grid belongs.

## Typography Rules
- **Display / headings:** `ui-serif, 'Iowan Old Style', 'Charter', Georgia, 'Times New Roman', serif`, weight 600
- **Body:** `-apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Text', system-ui, sans-serif`, weight 400
- **Mono:** `'JetBrains Mono', 'Geist Mono', 'IBM Plex Mono', ui-monospace, Menlo, monospace` — bento titles (`.mono-title`), index tabs (`01`–`04`), CLI pills, latency metrics
- Scale (px): 12.5 · 14 · 15.5 · 18 · 20 · 30–46 · 44–72 (clamped)
- Line-height: 1.55 body, 1.04–1.08 headings
- Letter-spacing: -0.028em on display sizes; +0.07em minimum on uppercase monospace labels
- Tabular numerics (`font-variant-numeric: tabular-nums`) everywhere numbers align

## Component Stylings
- **Buttons:** 6px radius, 11×20px padding; primary = `--accent` fill with `--accent-on` dark ink; secondary = transparent with `1px` `--border`
- **Bento Grid (`.bento-hairline`):** `gap: 1px; background: var(--border); border: 1px solid var(--border)` with flush `.bento-cell` panels and `.bento-visual` schematic stages
- **Studio / Runtime Window (`.app-window`):** 3-pane hairline-divided workspace with traffic lights, active canvas tab, and dot-matrix inspection pane
- **Index Showcase (`.index-showcase`):** Numbered `01`–`04` vertical monospace tab table paired with a framed command trace and vertical-line specification bullets

## Layout Principles
- Container 1180px, 32px gutters
- Hero: centered dual-tone headline + CTA row anchored by a full-width 3-pane `.app-window` across the fold
- Sections separated by `1px solid var(--border)` hairlines
- Desktop ≥ 921px: full multi-column hairline grids · Tablet/phone ≤ 920px: single-column collapse

## Depth & Elevation
- **Flat (0):** flush `.bento-cell` inside `.bento-hairline`
- **Specular (1):** `inset 0 1px 0 color-mix(in oklch, var(--fg) 8%, transparent)` on `.app-window`, `.bento-visual`, and `.card`

## Do's and Don'ts
- ✅ Anchor the hero with a multi-pane `.app-window` showing real workspace state
- ✅ Include bespoke inline SVG schematics (arc gauge, isometric volume cube, DAG node tree, wireframe globe) inside every `.bento-cell`
- ❌ Never ship a 3-column "small icon + heading + paragraph" feature grid
- ❌ No emojis, no invented marketing multipliers, no raw hex outside `:root`

## Responsive Behavior
- **Desktop > 920px:** 3-col `.bento-hairline`, 3-pane `.app-panes`, 3-col `.index-showcase`
- **Mobile/Tablet ≤ 920px:** all grids collapse cleanly to `1fr`

## Agent Prompt Guide
- Bind `:root` verbatim from this contract.
- Keep accent usage ≤ 2 visible moments per viewport.
- Every section must carry `data-design-id`.

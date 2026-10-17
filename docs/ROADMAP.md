# Roadmap

Where Design Studio is, and where it's heading. Directions, not promises.

## Shipped

### v1.0.0 — the core

- `DESIGN.md` brand contract + five curated visual directions
- Seeds for landing/app pages and slide decks
- Anti-slop linter (P0/P1/P2) built around the seven cardinal sins
- Deck runtime: keyboard / wheel / touch navigation, light–dark themes, print styles
- One-line installer that works for any Agent Skills–compatible agent

### v1.1.0 — the craft upgrade

- **Linter v2** — computed WCAG contrast for the core token pairs, static accessibility checks (`lang`, `alt`, labels, zoom, focus, headings), `--json` output
- **New references** — `motion.md`, `ux-flows.md`, `data-viz.md`, `ui-patterns.md`; upgraded `quality-gates.md`, `design-md.md`, `artifact-contract.md`
- **New seeds** — `dashboard-seed.html`, `mobile-seed.html` (device frame), `ui-patterns.html` (component states); section library grown to 10 blocks
- **Workflow** — experience dials (density / expressiveness / motion), review mode for audits, screenshot verification
- **Self-tests** — rule fixtures plus shipped-artifact regression checks

### v1.2.0 — flagship architecture (8 directions)

- Expanded `references/directions.md` from five (v1.0.0) to **8 curated visual directions** — added dark-native `dark-structural-grid`, `neo-brutalist-terminal`, `atmospheric-craft-dark` with `--accent-on` + `--surface-2`

### v1.2.1 — bug fixes

- `SKILL.md` resource map says 8 directions; flagship rules yield to an existing `DESIGN.md`
- New P1 `dashboard-missing-craft` lint check + fixture

### v1.3.0 — Agent-UX artifact kind

- New `agent` kind (`thread` / `run-detail` / `approval` / `activity`) with `references/agent-ux.md` contracts
- New `assets/agent-seed.html` + `assets/agent-ux-patterns.html`; agent lint gates (`tool-call-missing-status`, `destructive-without-approval`, `stream-missing-aria-live`); `demo/agent.html` incident-triage demo

## Next

- **Direction palettes v2** — extend each direction with a dark tier and accent alternates
- **More deck layouts** — comparison, timeline, and quote-wall slide skeletons
- **Chart library** — additional inline-SVG chart types (stacked bars, sparklines, heatmap)
- **Findings schema docs** — a stable, documented shape for `--json` so it can gate CI pipelines
- **Community gallery** — links to notable artifacts built with the skill

## Non-goals

- Runtime dependencies, build steps, or framework output — artifacts stay single-file HTML
- Multi-page apps with routing or backend logic
- A hosted service — the skill runs locally, offline, inside your agent

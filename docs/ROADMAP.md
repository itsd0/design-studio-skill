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

### v1.3.1 — Agent-UX quality pass

- Run header with Stop/Cancel + elapsed/tokens/cost; named destructive approvals; timeline done/current/pending states with connectors; muted success pills; Args + output on every active tool call; numbered full-border plan steps; icon/timestamp activity feed; sticky mobile approval bar; thread view in `demo/agent.html`
- New lint gates: `run-missing-stop` (P0), `destructive-approve-unnamed` (P0), `tool-call-missing-output` (P1), agent `accent-overuse` (P1)

### v1.3.2 — Agent-UX hotfix

- `minmax(0, 1fr)` collapse + `min-width: 0` children + mobile code-wrap (verified `scrollWidth === clientWidth` at 390px); stacked activity meta; Thread view after eval; new P1 `mobile-grid-1fr` lint gate + fixture

### v1.4.0 — enterprise-ready

- Pinned verified installs (`VERSION=` + `SHA256SUMS`), `SECURITY.md`, frozen `lint --json` v1 contract, CI + release automation, branch protection

### v1.4.1 — governance docs

- `CONTRIBUTING.md`, issue/PR templates, Code of Conduct, `docs/adopting.md`

### v1.5.0 — the render gate

- **`scripts/verify.py`** — loads an artifact in headless Chrome at 390px, 768px and 1440px and reports what source analysis cannot see: horizontal overflow (with the element that causes it), clipped text (with the culprit), computed contrast for every text run, tap targets under 24×24, runtime JS errors, missing image dimensions, missing focus indicators, missing/zoom-blocking viewport meta
- **`scripts/probe.js`** — the in-page probe: parses `color(srgb …)`, `oklch()` and `color-mix()` results, composites alpha backgrounds, applies the WCAG 2.2 inline and spacing exceptions for tap targets
- **Frozen `--json` contract** (`docs/verify-schema-v1.md`), pinned by a schema test
- **Rendered regression** — every shipped artifact must render clean; the section library is verified by composing it into the prototype seed (`tests/compose.py`)
- **CI `render` job** — the shipped artifacts and the composed library must render with zero P0/P1
- **Real defects fixed in the shipped files** — sideways scroll at 390px in the landing page, a clipped trace log, accent-coloured small text failing AA in three seeds, a white-on-accent button at 3.9:1, an unstyled blue link on a dark surface, and six controls under the 24×24 tap target

## Next

- **Contract fidelity** — parse `DESIGN.md` and diff its tokens, section order and dials against the artifact, so "DESIGN.md is the contract" becomes a mechanical P0 gate instead of a prose instruction
- **Linter v3** — parse the DOM (stdlib `html.parser`) so structural rules are precise rather than approximated: duplicate ids, button/link names, `target="_blank"` without `rel`, `tabindex > 0`, landmarks, table header scope
- **Direction palettes v2** — extend each direction with a dark tier and accent alternates, as machine-readable `directions.json`
- **More deck layouts** — comparison, timeline, and quote-wall slide skeletons
- **Chart library** — additional inline-SVG chart types (stacked bars, sparklines, heatmap)
- **Brief manifest** — `brief.json` recording must-keep facts, so "no invented metrics" is mechanically enforced
- **Community gallery** — links to notable artifacts built with the skill

## Non-goals

- Runtime dependencies, build steps, or framework output — artifacts stay single-file HTML
- Multi-page apps with routing or backend logic
- A hosted service — the skill runs locally, offline, inside your agent

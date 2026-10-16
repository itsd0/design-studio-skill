# Direction library — 8 curated visual directions (2025–2026 Flagship Edition)

Used when there is no brand to match, or when establishing a new product's visual architecture. Pick the best fit for the brief's domain and bind the palette and font stacks into the seed's `:root` **verbatim**. Each direction is deliberately distinct — do not blend two.

For **AI infrastructure, developer tools, agent runtimes, cloud platforms, and technical SaaS**, prefer **Directions 1, 2, or 3** (the 2025–2026 dark-native flagship wave) unless the user requests a light surface.

Palettes are OKLch values (modern browsers support `oklch()` and the seeds use `color-mix(in oklch, ...)` already). Every direction defines `--accent-on` so primary buttons and solid highlight blocks always pass WCAG contrast whether `--accent` is a luminous signal tone or a deep ink tone.

---

## 1 · Dark Structural Grid — Swiss-Grid DevTool & AI Infra  `(id: dark-structural-grid)`

**Use for:** AI agent infrastructure, cloud sandboxes, developer platforms, observability, databases, SDKs, high-velocity technical products.
**Mood:** Precision-engineered, architectural, telemetry-first. Exposed `1px` hairline structural grids (`gapless bento`), dual-tone headlines (crisp white + slate grey), monospace structural chrome, and interactive-looking schematic diagrams (DAG node pipelines, latency gauges, wireframe globes, isometric volume layers).
**References:** Linear, Vercel Geist, Cursor, Raycast, Supabase, modern 2025–2026 AI infra platforms.

```css
:root {
  --bg:        oklch(13% 0.006 255);   /* obsidian canvas */
  --surface:   oklch(16% 0.008 255);   /* flush bento cells, terminal panes */
  --surface-2: oklch(20% 0.010 255);   /* raised controls, active pills, code headers */
  --fg:        oklch(96% 0.004 255);   /* primary headline & crisp UI text */
  --muted:     oklch(68% 0.012 255);   /* secondary lead-ins, dual-tone headline half */
  --border:    oklch(24% 0.010 255);   /* exposed 1px structural hairlines */
  --accent:    oklch(80% 0.17 152);    /* phosphor signal green */
  --accent-on: oklch(15% 0.02 152);    /* dark ink on phosphor CTA buttons */

  --font-display: -apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', system-ui, sans-serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Text', system-ui, sans-serif;
  --font-mono:    'JetBrains Mono', 'Geist Mono', 'IBM Plex Mono', ui-monospace, Menlo, monospace;

  --radius:    6px;
  --radius-lg: 10px;
}
```

**Posture:**
- **Exposed hairline grid architecture:** Use `.bento-hairline` (`gap: 1px; background: var(--border)`) and full-height vertical container rails (`.rail-container`) with corner crosshair `+` ticks instead of floating drop-shadow cards.
- **Dual-tone headlines:** Split `h1`/`h2` hierarchy using lightness (`<span class="tone-muted">Fast, Scalable, Stateful</span> Infrastructure for AI Agents.`) rather than font size alone.
- **Schematic bento visuals:** Every feature cell contains a bespoke inline SVG or HTML schematic (latency gauge, DAG node pipeline, isometric stack, or snapshot timeline) — never 3 small icons above paragraphs.
- **Monospace telemetry:** Card titles, coordinates, latency numbers, and status pills use `var(--font-mono)` with `font-variant-numeric: tabular-nums`.

---

## 2 · Neo-Brutalist Terminal — Industrial Agentic & CLI Platform  `(id: neo-brutalist-terminal)`

**Use for:** Agentic toolchains, API gateways, MCP/tool ecosystems, autonomous coding harnesses, security/crypto infrastructure, developer manifestos.
**Mood:** Raw industrial authority. Carbon black canvas, razor-sharp `0px` corners, solid high-contrast accent block highlights behind headline punchlines, compartmentalized `1px` navbars, numbered `01`–`04` monospace index tables, and floating dark CLI command cards over textured accent stages.
**References:** Modern agentic tool hubs, Swiss industrial terminal interfaces, teenage engineering × dark CLI.

```css
:root {
  --bg:        oklch(12% 0.004 260);   /* carbon black */
  --surface:   oklch(16% 0.006 260);   /* command cards, index cells */
  --surface-2: oklch(21% 0.008 260);   /* active index row, badge fill */
  --fg:        oklch(97% 0.003 260);   /* stark white */
  --muted:     oklch(68% 0.010 260);   /* technical slate */
  --border:    oklch(25% 0.008 260);   /* crisp structural hairlines */
  --accent:    oklch(62% 0.22 262);    /* electric cobalt / Klein signal blue */
  --accent-on: oklch(98% 0.003 260);   /* stark white on electric blue block */

  --font-display: -apple-system, BlinkMacSystemFont, 'Inter', 'Helvetica Neue', system-ui, sans-serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'Inter', system-ui, sans-serif;
  --font-mono:    'JetBrains Mono', 'IBM Plex Mono', ui-monospace, Menlo, monospace;

  --radius:    0px;
  --radius-lg: 2px;
}
```

**Posture:**
- **Zero-radius precision (`0px`–`2px`):** Buttons, nav compartments, index tabs, and cards use sharp architectural corners.
- **Solid block headline highlight:** Wrap the 2–3 word value punchline of `h1` in `<mark class="tone-block">` (`background: var(--accent); color: var(--accent-on); padding: 0 0.18em`).
- **Numbered index navigation (`01` / `02` / `03` / `04`):** Feature deep-dives use a left-hand `1px` bordered monospace index table paired with a framed command-palette / agent-plan visual stage.
- **Uppercase monospace chrome:** Nav links, CTAs, and badges use `var(--font-mono)`, uppercase, `letter-spacing: 0.08em`.

---

## 3 · Atmospheric Craft Dark — Painterly Hero & Native Studio UI  `(id: atmospheric-craft-dark)`

**Use for:** Design-to-code engines, creative AI studios, macOS/desktop developer apps, flagship prosumer tools, next-gen IDEs.
**Mood:** Romantic realism meets precision dark software. A moody, atmospheric canvas backdrop in the hero fading seamlessly into deep obsidian, paired with sculpted display typography, a luminous mint/sage CTA, and a multi-pane desktop app / IDE canvas anchored across the fold.
**References:** Flagship AI design studios, native macOS pro tools, Zed, Linear releases, Lusion-grade product showcases.

```css
:root {
  --bg:        oklch(14% 0.008 155);   /* deep botanical obsidian */
  --surface:   oklch(18% 0.010 155);   /* IDE window chrome, studio panels */
  --surface-2: oklch(22% 0.012 155);   /* active project row, prompt bubble, canvas tab */
  --fg:        oklch(96% 0.005 110);   /* warm alabaster white */
  --muted:     oklch(70% 0.014 145);   /* muted sage-slate */
  --border:    oklch(25% 0.012 155);   /* subtle window & pane dividers */
  --accent:    oklch(82% 0.15 150);    /* luminous studio mint */
  --accent-on: oklch(15% 0.02 150);    /* deep obsidian ink on mint buttons */

  --font-display: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', system-ui, sans-serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Inter', system-ui, sans-serif;
  --font-mono:    'JetBrains Mono', 'SF Mono', ui-monospace, Menlo, monospace;

  --radius:    8px;
  --radius-lg: 12px;
}
```

**Posture:**
- **Hero + Studio App Stage:** The hero pairs a centered high-taste headline and luminous CTA with an immediately visible **3-pane Studio/IDE Window** (`.app-window`: left project tree with traffic-light dots, center prompt/reasoning stream, right `.canvas` dot-grid inspection surface).
- **Specular top-edge border:** Studio windows and raised surfaces carry a subtle 1px top highlight (`box-shadow: inset 0 1px 0 color-mix(in oklch, var(--fg) 10%, transparent)`).
- **Restrained atmospheric depth:** Use `.hero-atmosphere` (radial/vignette tonal depth derived from `--accent-soft` and `--bg`) behind the hero only; keep all lower sections crisp and obsidian-flat.

---

## 4 · Editorial — Monocle / FT Magazine  `(id: editorial-monocle)`

**Use for:** Explicitly editorial, research labs, essays, publishing, or thought-leadership briefs. **Not** for dark consoles or utility dashboards.
**Mood:** Print-magazine authority. Generous whitespace, large serif headlines, restrained palette of neutral paper + deep ink + one brand-justified editorial accent.
**References:** Monocle, FT Weekend, Stripe Press, Anthropic research index.

```css
:root {
  --bg:        oklch(98% 0.004 95);    /* neutral paper, not peach wash */
  --surface:   oklch(100% 0.002 95);
  --surface-2: oklch(95% 0.006 95);
  --fg:        oklch(20% 0.018 70);    /* deep ink */
  --muted:     oklch(48% 0.012 70);
  --border:    oklch(89% 0.006 95);
  --accent:    oklch(50% 0.14 28);     /* restrained editorial vermilion */
  --accent-on: oklch(99% 0.002 95);

  --font-display: 'Iowan Old Style', 'Charter', 'Newsreader', Georgia, serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  --font-mono:    ui-monospace, 'JetBrains Mono', Menlo, monospace;

  --radius:    4px;
  --radius-lg: 8px;
}
```

**Posture:** Serif display, sans body, mono metadata only · no drop shadows — crisp `1px` rules + architectural whitespace do the work · numbered essay/figure callouts · eyebrow in mono uppercase, accent used at most twice.

---

## 5 · Modern Minimal Light — Linear Light / Vercel / Stripe  `(id: modern-minimal)`

**Use for:** B2B SaaS, fintech, productivity suites, clean documentation, light-mode developer products.
**Mood:** Quiet, surgical, product-led. High-craft daylight surfaces with exposed hairline grids, crisp neutral foundations, and interactive product frames.
**References:** Linear (Light), Vercel Geist, Stripe, Notion, Chronicle.

```css
:root {
  --bg:        oklch(99% 0.002 240);
  --surface:   oklch(100% 0 0);
  --surface-2: oklch(96% 0.004 240);
  --fg:        oklch(16% 0.012 250);
  --muted:     oklch(50% 0.012 250);
  --border:    oklch(90% 0.005 250);
  --accent:    oklch(52% 0.19 255);    /* precision cobalt */
  --accent-on: oklch(99% 0.002 240);

  --font-display: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', system-ui, sans-serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Inter', system-ui, sans-serif;
  --font-mono:    ui-monospace, 'JetBrains Mono', Menlo, monospace;

  --radius:    8px;
  --radius-lg: 12px;
}
```

**Posture:** Tight tracking on display sizes (`-0.025em`) · dual-tone headlines (`--fg` + `--muted`) · `.bento-hairline` feature grids with embedded UI schematics · mono numerics with `font-variant-numeric: tabular-nums` · sticky frosted nav.

---

## 6 · Human / Approachable — Mercury / Airbnb / Craft  `(id: human-approachable)`

**Use for:** Consumer products, financial operations, marketplaces, collaborative workspaces, AI assistants.
**Mood:** Tactile, warm, and sculpted without generic pastel slop. Crisp stone/alabaster canvas, high-craft UI cards, generous radii, clear hierarchy.
**References:** Mercury, Airbnb, Amie, Readwise Reader.

```css
:root {
  --bg:        oklch(98% 0.004 240);
  --surface:   oklch(100% 0 0);
  --surface-2: oklch(95% 0.006 240);
  --fg:        oklch(20% 0.02 240);
  --muted:     oklch(48% 0.018 240);
  --border:    oklch(90% 0.006 240);
  --accent:    oklch(48% 0.13 170);    /* deep mineral teal */
  --accent-on: oklch(99% 0.002 240);

  --font-display: 'Söhne', 'Avenir Next', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'SF Pro Text', system-ui, sans-serif;
  --font-mono:    ui-monospace, Menlo, monospace;

  --radius:    10px;
  --radius-lg: 16px;
}
```

**Posture:** Sans display with strong weight contrast · radii 10–16px on a structured bento grid · interactive UI widgets inside feature cards (live ledger rows, command pills, status timelines) · never flood pages with pastel gradients.

---

## 7 · Tech / Utility Light — Datadog / GitHub / Cloudflare  `(id: tech-utility)`

**Use for:** Daylight engineering consoles, infrastructure docs, status pages, control planes, local-first CLI tools.
**Mood:** Data-dense, blueprint-clean, monospace-forward. High information per square inch on a crisp technical paper canvas.
**References:** Cloudflare dashboard, GitHub, Sentry, Tailscale.

```css
:root {
  --bg:        oklch(98% 0.005 250);
  --surface:   oklch(100% 0 0);
  --surface-2: oklch(95% 0.007 250);
  --fg:        oklch(20% 0.02 240);
  --muted:     oklch(48% 0.018 240);
  --border:    oklch(89% 0.008 240);
  --accent:    oklch(50% 0.16 145);    /* high-contrast signal green */
  --accent-on: oklch(99% 0.002 250);

  --font-display: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', system-ui, sans-serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', system-ui, sans-serif;
  --font-mono:    'JetBrains Mono', 'IBM Plex Mono', ui-monospace, Menlo, monospace;

  --radius:    6px;
  --radius-lg: 10px;
}
```

**Posture:** One geometric sans family for display + body · tabular numerics everywhere; mono for commands, IDs, latency, hashes · exposed `1px` structural grids (`.bento-hairline`) and `.bg-grid-matrix` blueprint backgrounds · live terminal/telemetry previews above the fold.

---

## 8 · Brutalist / Experimental — Are.na / US Graphics / Yale  `(id: brutalist-experimental)`

**Use for:** Design studios, hardware/industrial specs, creative manifestos, experimental developer tools.
**Mood:** Loud typographic scale, exposed full-strength `1.5px` ink grid rules, datasheet specifications, deliberate mechanical confidence.
**References:** U.S. Graphics Company, Are.na, Teenage Engineering datasheets, Yale School of Art.

```css
:root {
  --bg:        oklch(97% 0.006 95);    /* technical specification paper */
  --surface:   oklch(100% 0 0);
  --surface-2: oklch(93% 0.008 95);
  --fg:        oklch(15% 0.02 100);
  --muted:     oklch(42% 0.02 100);
  --border:    oklch(15% 0.02 100);    /* borders are full-strength ink */
  --accent:    oklch(54% 0.21 27);     /* industrial international orange-red */
  --accent-on: oklch(99% 0.002 95);

  --font-display: 'Times New Roman', 'Iowan Old Style', Georgia, serif;
  --font-body:    ui-monospace, 'IBM Plex Mono', 'JetBrains Mono', Menlo, monospace;
  --font-mono:    ui-monospace, 'IBM Plex Mono', 'JetBrains Mono', Menlo, monospace;

  --radius:    0px;
  --radius-lg: 0px;
}
```

**Posture:** Extreme display sizes (`clamp(64px, 10vw, 140px)`) · body = monospace · full-strength `1px–1.5px` ink borders · asymmetric specification tables and numbered index blocks · `0px` border-radius everywhere, no shadows, no gradients.

---

## Binding rules

- Bind the chosen direction's palette and fonts **verbatim**. Never improvise values from the label.
- Always include `--accent-on` and `--surface-2` in `:root` so buttons, badges, and multi-pane product previews render with high-end contrast.
- Honor the posture cues in layout decisions — especially **exposed hairline grids (`.bento-hairline`)**, **dual-tone headlines**, and **embedded product/schematic visuals** — they are what makes the direction read as a 2025–2026 flagship product rather than a palette swap.
- State the chosen direction in one sentence before building: `Direction: dark-structural-grid (phosphor green on obsidian, exposed hairline bento + live telemetry schematics).`

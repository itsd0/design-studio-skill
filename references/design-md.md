# DESIGN.md — the brand contract

`DESIGN.md` is the single source of brand truth for every artifact. It is prose for humans and agents; `tokens.css` is the machine-readable twin. Every artifact binds the token block verbatim and never invents values.

## Contract shape

```
design-systems/<slug>/
├── manifest.json     # id / name / category / description / provenance   (catalog packages)
├── DESIGN.md         # canonical design prose for agents                 (required)
└── tokens.css        # canonical compiled semantic-token stylesheet      (required)
```

For a standalone project, a single `DESIGN.md` in the working directory is enough. Legacy folders with only `DESIGN.md` remain valid.

## Required sections (in order)

1. **Title + meta blockquote** — `# Brand Name`, then `> Category:` and one-sentence "use when".
2. **Visual Theme & Atmosphere** — 2–3 sentences of mood. Concrete, not vibes ("Calm, functional, quietly confident. No ornament.").
3. **Experience Dials** — density / expressiveness / motion, one level each (see below). Recommended for every new brand.
4. **Color Palette & Roles** — every color with a role, never a bare swatch list.
5. **Typography Rules** — display / body / mono stacks, weights, px scale, line-height, tracking notes.
6. **Component Stylings** — buttons, cards, inputs, links: radius, padding, fill, border, states.
7. **Layout Principles** — grid, max-width, gutters, section spacing per breakpoint, separators.
8. **Depth & Elevation** — named levels only (e.g. flat 0 / raised 1 with exact shadow recipe). No improvised shadows.
9. **Do's and Don'ts** — checkable bullets, including the palette's anti-patterns.
10. **Responsive Behavior** — desktop / tablet / phone column counts, gutters, hero changes.
11. **Agent Prompt Guide** — the tiebreaker rules for ambiguous cases ("When in doubt, subtract.").

## Experience dials

Three 3-level dials capture the brief's posture. They are **recorded, not vibes** — an artifact's choices must match its recorded levels:

| Dial | Levels | What it changes |
|---|---|---|
| Density | `airy` · `regular` · `compact` | section-y steps (default 80/48/32; compact 48/32/24), row heights, whitespace budget |
| Expressiveness | `restrained` · `assured` · `bold` | composition risk (grid-breaks, overlap, scale jumps), how loud the single flourish may get |
| Motion | `still` · `standard` · `lively` | micro-interaction count (0–1–2), entrance choreography on/off, durations within `motion.md`'s table |

A `bold` brand ships one grid-break or overlap moment; a `restrained` one ships none, however tempting. A `still` brand ships zero entrance animation, full stop.

## Standard token names (tokens.css)

Bind `:root` to these names — components across brands resolve uniformly:

```css
:root {
  /* surface — never pure black, never pure white */
  --bg: #fafafa;
  --surface: #ffffff;
  --surface-warm: var(--surface);        /* optional tertiary tier */

  /* foreground ramp */
  --fg: #111111;
  --fg-2: var(--fg);                     /* optional secondary tier */
  --muted: #6b6b6b;
  --meta: var(--muted);                  /* optional metadata tier */

  /* borders */
  --border: #e5e5e5;
  --border-soft: var(--border);

  /* accent — one per brand; hover/active are part of the contract */
  --accent: #2f6feb;
  --accent-on: #ffffff;                  /* text on accent fill */
  --accent-hover: color-mix(in oklab, var(--accent), black 8%);
  --accent-active: color-mix(in oklab, var(--accent), black 14%);

  /* semantic — state only, <5% of pixels */
  --success: #17a34a;
  --warn: #eab308;
  --danger: #dc2626;

  /* type */
  --font-display: "Inter", system-ui, sans-serif;
  --font-body: "Inter", system-ui, sans-serif;
  --font-mono: ui-monospace, "JetBrains Mono", monospace;
  --text-xs: 12px;  --text-sm: 14px;  --text-base: 16px; --text-lg: 20px;
  --text-xl: 24px;  --text-2xl: 32px; --text-3xl: 48px;  --text-4xl: 64px;
  --leading-body: 1.5;
  --leading-tight: 1.2;
  --tracking-display: -0.01em;

  /* spacing — 4px base */
  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px;
  --space-5: 20px; --space-6: 24px; --space-8: 32px; --space-12: 48px; --space-20: 80px;
  --section-y-desktop: 80px;
  --section-y-tablet: 48px;
  --section-y-phone: 32px;

  /* radius — two intents, plus pill */
  --radius-sm: 8px; --radius-md: 12px; --radius-lg: 16px; --radius-pill: 9999px;

  /* elevation — three levels max */
  --elev-flat: none;
  --elev-ring: 0 0 0 1px var(--border);
  --elev-raised: 0 2px 8px color-mix(in oklab, var(--fg), transparent 92%);

  /* interaction */
  --focus-ring: 0 0 0 3px color-mix(in oklab, var(--accent), transparent 70%);
  --motion-fast: 150ms;
  --motion-base: 200ms;
  --ease-standard: cubic-bezier(0.2, 0, 0, 1);

  /* layout */
  --container-max: 1200px;
}
```

The six values every artifact must be able to answer: **bg, surface, fg, muted, border, accent**. The rest are additive tiers — shallow brands alias them (`--fg-2: var(--fg)`) rather than inventing values.

A brand may define a **dark tier** — the same token names redeclared for `@media (prefers-color-scheme: dark)`. The linter computes contrast for every theme scope it finds in an artifact.

## Authoring rules

- **Never pure black or pure white.** Dark themes: `#0f0f0f` bg / `#f0f0f0` fg. Light: `#fafafa` / `#111111`.
- **One accent.** Named by purpose, never by hue (`--accent`, not `--blue-500`). Hover/active variants ship with every brand.
- **Keep the token names.** New brands overwrite values, not keys. Extend additively.
- **Colors carry roles.** "Accent — primary CTAs, links, one hero element per screen", not "Blue #2F6FEB".
- **Dials are part of the contract.** Record density / expressiveness / motion; artifacts at `still` ship zero entrance animation, artifacts at `airy` never use the compact spacing step.
- **Every rule must be checkable.** "Cards: white, 1px border, 12px radius, no shadow" — not "cards feel airy".
- **Include an Agent Prompt Guide.** The tiebreaker rules agents apply when the brief is ambiguous.
- **Anti-patterns are first-class.** List what NOT to do (gradients, shadows on inputs, >3 type sizes per screen).

## Deriving a DESIGN.md from a brand source

1. **Sample the six core tokens** from the source (logo, site CSS, screenshot): bg, surface, fg, muted, border, accent. Note the accent's true hue before any UI safelights it.
2. **Identify the type stack**: display face, body face, mono; weights used (typically 3: read / emphasize / announce).
3. **Describe the posture** in 3–5 concrete bullets: radius family, border weight, shadow usage, spacing density, imagery style.
4. **Set the dials** from the brief, not from taste habit: a government service does not get `bold` expressiveness because the palette is nice.
5. **Write the Do's / Don'ts** from observed patterns plus the universal craft rules in `references/quality-gates.md`.
6. **Fill the Agent Prompt Guide** with the decisions most likely to be gotten wrong for this brand.
7. **Check contrast with the linter, not by eye** — `python3 scripts/lint.py` computes the core pairs (and any dark tier) and prints the ratios.

Unknowns stay honest: mark them `[REPLACE]` or omit the tier — never fabricate a brand value.

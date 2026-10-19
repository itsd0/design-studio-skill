# Light Editorial Serif

**Use it for:** research products, newsletters, long-form writing tools, studio
sites, anything whose content is the point.

**Why it works:** a serif display face against a warm paper ground reads as
*considered* before a word is read, and the terracotta accent is warm enough
to live on cream without shouting.

## Tokens

```css
:root {
  --bg:        oklch(98% 0.006 85);
  --surface:   oklch(99% 0.004 85);
  --surface-2: oklch(95% 0.010 85);
  --fg:        oklch(22% 0.012 60);
  --muted:     oklch(48% 0.014 60);
  --border:    oklch(88% 0.012 80);
  --accent:    oklch(52% 0.14 35);
  --accent-on: oklch(98% 0.006 85);
  --accent-soft: color-mix(in oklch, var(--accent) 12%, transparent);
  --fg-soft:     color-mix(in oklch, var(--fg) 6%, transparent);

  --font-display: 'Iowan Old Style', 'Charter', Georgia, 'Times New Roman', serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'Inter', system-ui, sans-serif;
  --font-mono:    ui-monospace, 'SF Mono', Menlo, monospace;

  --radius: 4px;
  --gap: 24px;
}
```

## Type

| Role | Size | Family | Notes |
|---|---|---|---|
| Display (h1) | 52–80px | serif | line-height 1.02, tracking −0.03em |
| Section (h2) | 34–44px | serif | line-height 1.08 |
| Lead | 19–21px | body | line-height 1.55, max 62ch |
| Body | 16–17px | body | line-height 1.6 |
| Label | 11–12px | mono | uppercase, +0.09em |

Serif headlines are the whole point. If the display face is a grotesk, this
grammar is not this grammar.

## Layout

- Container 1120px, 40px gutters, asymmetric — a wide measure for prose
  (62ch) inside a narrower grid.
- Section spacing 120px desktop / 72px phone. Airy is the default.
- Rules are `1px solid var(--border)`, full-measure, and rare.
- A pull quote breaks the measure: 1.4× the body size, serif, no card.

## Component recipes

**Editorial rule + meta row:**

```css
.rule { height: 1px; background: var(--border); border: 0; margin: 0; }
.meta-row { display: flex; justify-content: space-between; gap: 24px;
  font-family: var(--font-mono); font-size: 11px; letter-spacing: .08em;
  text-transform: uppercase; color: var(--muted); flex-wrap: wrap; }
```

**Pull quote:**

```css
.pull { font-family: var(--font-display); font-size: clamp(24px, 3vw, 34px);
  line-height: 1.25; letter-spacing: -.02em; margin: 0;
  border-top: 2px solid var(--accent); padding-top: 20px; }
```

**Table** — hairline, no fills, prose in the second column:

```css
.editorial-table { width: 100%; border-collapse: collapse; font-size: 15px; }
.editorial-table th { text-align: left; font-family: var(--font-mono);
  font-size: 11px; letter-spacing: .07em; text-transform: uppercase;
  color: var(--muted); font-weight: 500; padding: 12px 16px;
  border-bottom: 1px solid var(--fg); }
.editorial-table td { padding: 14px 16px; border-bottom: 1px solid var(--border);
  vertical-align: top; }
```

Wrap a wide table in `.tablewrap { overflow-x: auto; }` — a prose table cannot
shrink below its longest word, and a table that pushes the page sideways is a
bug on every platform.

## Anti-patterns

- ❌ A grotesk display face. The serif *is* the identity.
- ❌ Pure white `#fff` paper, or pure black text.
- ❌ Centred everything. Editorial has a left edge and means it.
- ❌ More than one accent moment per screen.
- ❌ A three-icon feature grid — use a rule-separated list instead.

## Verified example

`assets/section-skeletons.html` (the `compare` and `quote` sections) plus the
`Paper Editorial` direction in `references/directions.md` follow this grammar.

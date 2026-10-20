# Arctic Precision

**Use it for:** scientific instruments, hardware, aerospace, medical devices,
developer tools that want to feel *measured*.

**Why it works:** ice-white ground, a single cold blue, and a hairline that never
gets thicker than 1px. Everything is calibrated; nothing is decorative.

## Tokens

```css
:root {
  --bg:        oklch(99% 0.004 230);
  --surface:   oklch(100% 0 0);
  --surface-2: oklch(95% 0.01 230);
  --fg:        oklch(24% 0.02 245);
  --muted:     oklch(52% 0.02 240);
  --border:    oklch(88% 0.015 235);
  --accent:    oklch(52% 0.13 235);
  --accent-on: oklch(99% 0.004 230);

  --font-display: -apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', system-ui, sans-serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Text', system-ui, sans-serif;
  --font-mono:    'JetBrains Mono', 'IBM Plex Mono', ui-monospace, Menlo, monospace;

  --radius: 4px;
  --gap: 16px;
}
```

## Type

| Role | Size | Weight | Notes |
|---|---|---|---|
| Display (h1) | 30–44px | 600 | tracking −0.02em |
| Section (h2) | 18–22px | 600 | |
| Body | 14–15px | 400 | line-height 1.55 |
| Data | 12–13px | 500 | mono, `tabular-nums` |
| Label | 10.5px | 600 | mono, uppercase, +0.09em |

Labels are mono and tiny — they read as *instrument markings*, not UI text.

## Layout

- Container 1160px, 24px gutters. Dense but never cramped.
- Gapless hairline grids: `gap: 1px; background: var(--border)`.
- Every number sits in a mono cell with a unit; every axis is labelled.
- Diagrams are schematic (inline SVG), never illustrative.

## Component recipes

**Instrument cell:**

```css
.cell { background: var(--surface); padding: 16px 18px;
  display: flex; flex-direction: column; gap: 6px; }
.cell .k { font-family: var(--font-mono); font-size: 10.5px; letter-spacing: .09em;
  text-transform: uppercase; color: var(--muted); }
.cell .v { font-family: var(--font-mono); font-size: 20px; font-variant-numeric: tabular-nums; }
```

**Hairline grid:**

```css
.grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1px; background: var(--border); border: 1px solid var(--border);
  border-radius: var(--radius); overflow: hidden; }
@media (max-width: 920px) { .grid { grid-template-columns: minmax(0, 1fr); } }
```

## Anti-patterns

- ❌ Warm greys or cream — the ground is cold.
- ❌ Shadows. Elevation is a hairline, not a blur.
- ❌ Sans body above 15px — precision reads small.
- ❌ Icons where a label would be clearer.
- ❌ Decorative imagery. Schematics only.

## Verified example

`assets/dashboard-seed.html` is the closest shipped grammar; its hairline KPI
strip is the pattern to copy.

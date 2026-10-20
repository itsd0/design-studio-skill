# Clinical Data

**Use it for:** dashboards of measurements — finance, lab results, operations,
medical, anything where a number is the product.

**Why it works:** a cool near-white ground, one teal signal and a strict type
scale let the numbers dominate. Nothing competes with the data.

## Tokens

```css
:root {
  --bg:        oklch(99% 0.002 200);
  --surface:   oklch(100% 0 0);
  --surface-2: oklch(96% 0.006 200);
  --fg:        oklch(26% 0.02 220);
  --muted:     oklch(54% 0.02 220);
  --border:    oklch(91% 0.008 210);
  --accent:    oklch(52% 0.11 195);
  --accent-on: oklch(99% 0.002 200);
  --accent-soft: color-mix(in oklch, var(--accent) 10%, transparent);
  --fg-soft:     color-mix(in oklch, var(--fg) 5%, transparent);

  --font-display: -apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', system-ui, sans-serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Text', system-ui, sans-serif;
  --font-mono:    ui-monospace, 'SF Mono', Menlo, monospace;

  --radius: 8px;
  --gap: 16px;
}
```

## Type

| Role | Size | Notes |
|---|---|---|
| KPI value | 30–40px | mono, `tabular-nums`, weight 600, tracking −0.02em |
| Display (h1) | 26–32px | weight 600, tracking −0.02em |
| Section (h2) | 17–20px | weight 600 |
| Body | 14–15px | line-height 1.5 |
| Axis / label | 11–12px | mono, +0.05em, muted |

Numbers are always mono with tabular figures. A dashboard whose figures
change width as they update is unreadable at a glance.

## Layout

- Rail on the left (208px) collapses to a horizontal scroller under 920px.
- A KPI row: 3–5 values, hairline divided, no cards.
- Charts live in a panel with a title row and an explicit time range.
- Density is **regular**; whitespace is a tool, not a style.

## Component recipes

**KPI row** — hairline divided, no cards:

```css
.kpis { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1px; background: var(--border); border: 1px solid var(--border);
  border-radius: var(--radius); overflow: hidden; }
.kpi { background: var(--surface); padding: 18px 20px; }
.kpi .label { font-family: var(--font-mono); font-size: 11px; letter-spacing: .06em;
  text-transform: uppercase; color: var(--muted); }
.kpi .value { font-family: var(--font-mono); font-size: 30px; font-weight: 600;
  font-variant-numeric: tabular-nums; letter-spacing: -.02em; margin-top: 6px; }
```

**Panel with a title row:**

```css
.panel { background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); }
.panel-head { display: flex; align-items: center; justify-content: space-between;
  gap: 16px; padding: 14px 18px; border-bottom: 1px solid var(--border); }
.panel-head h2 { font-size: 16px; font-weight: 600; margin: 0; }
```

**Data table** — a real table, with a scroll container:

```css
.tablewrap { overflow-x: auto; }
.dt { width: 100%; border-collapse: collapse; font-size: 13.5px; }
.dt th { text-align: left; font-family: var(--font-mono); font-size: 11px;
  letter-spacing: .06em; text-transform: uppercase; color: var(--muted);
  font-weight: 500; padding: 10px 14px; border-bottom: 1px solid var(--border); }
.dt td { padding: 12px 14px; border-bottom: 1px solid var(--border);
  font-variant-numeric: tabular-nums; }
.dt .num { text-align: right; font-family: var(--font-mono); }
```

## Anti-patterns

- ❌ A KPI with a coloured sparkline *and* a coloured value *and* a coloured
  delta. One signal per number.
- ❌ Saturated chart palettes. Two series need two colours, not ten.
- ❌ Inconsistent decimals across a column. Pick a format and hold it.
- ❌ A chart without units, a range, or a source line.
- ❌ Rounded corners above 8px on data surfaces.

## Verified example

`assets/dashboard-seed.html` and `demo/dashboard.html` follow this grammar and
pass the three gates clean.

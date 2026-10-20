# Trading Desk

**Use it for:** trading, monitoring, on-call, logistics — anything where the
operator stares at numbers and the cost of a missed signal is real.

**Why it works:** maximum density, zero decoration, and red/green reserved for
direction. Nothing on screen is allowed to be merely pretty.

## Tokens

```css
:root {
  --bg:        oklch(12% 0.008 250);
  --surface:   oklch(15% 0.008 250);
  --surface-2: oklch(19% 0.01 250);
  --fg:        oklch(94% 0.004 250);
  --muted:     oklch(64% 0.01 250);
  --border:    oklch(26% 0.01 250);
  --accent:    oklch(80% 0.14 200);
  --accent-on: oklch(14% 0.02 250);
  --up:        oklch(72% 0.17 150);
  --down:      oklch(66% 0.19 25);

  --font-display: -apple-system, BlinkMacSystemFont, 'Inter', system-ui, sans-serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'Inter', system-ui, sans-serif;
  --font-mono:    'JetBrains Mono', ui-monospace, Menlo, monospace;

  --radius: 2px;
  --gap: 8px;
}
```

## Type

| Role | Size | Notes |
|---|---|---|
| Display (h1) | 18–22px | weight 600 — this is a tool, not a poster |
| Table header | 10.5px | mono, uppercase, +0.08em |
| Row | 12–13px | mono, `tabular-nums` |
| Value | 15–18px | mono, weight 600 |

Display type is *small*. A trading screen with a 48px headline wastes the
operator's field of view.

## Layout

- Full-width, 8px gutters, no container max-width beyond 1600px.
- Rows are 28–32px. A viewport should hold 20+ rows.
- Sticky headers and a sticky column of identifiers.
- Red/green only for direction or state; never for brand.
- Tables scroll inside their own box, never the page.

## Component recipes

**Dense row:**

```css
.row { display: grid; grid-template-columns: 120px 1fr 96px 96px 72px;
  gap: 8px; align-items: center; height: 30px; padding: 0 10px;
  border-bottom: 1px solid var(--border); font-family: var(--font-mono);
  font-size: 12.5px; font-variant-numeric: tabular-nums; }
.row:hover { background: var(--surface-2); }
.row .up { color: var(--up); }
.row .down { color: var(--down); }
```

**Sticky header:**

```css
.thead { position: sticky; top: 0; z-index: 2; background: var(--surface);
  border-bottom: 1px solid var(--border); }
```

## Anti-patterns

- ❌ Big marketing type. This is a tool.
- ❌ Cards around rows — a table is a table.
- ❌ Red/green for anything other than direction or state.
- ❌ Row heights above 36px, or padding that costs a visible row.
- ❌ Animated transitions on price changes longer than 150ms.

## Verified example

`demo/dashboard.html` is the consumer-grade sibling; this grammar is its denser
cousin. `scripts/verify.py` checks that the density does not break tap targets.

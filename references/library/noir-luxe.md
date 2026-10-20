# Noir Luxe

**Use it for:** watches, spirits, private client services, jewellery, anything
that should feel expensive before it is read.

**Why it works:** black, one warm metal, and a high-contrast serif set large.
The restraint is the price signal.

## Tokens

```css
:root {
  --bg:        oklch(11% 0.004 60);
  --surface:   oklch(15% 0.006 60);
  --surface-2: oklch(20% 0.008 60);
  --fg:        oklch(94% 0.008 80);
  --muted:     oklch(66% 0.012 75);
  --border:    oklch(28% 0.012 70);
  --accent:    oklch(78% 0.11 85);
  --accent-on: oklch(12% 0.01 70);

  --font-display: 'Didot', 'Bodoni 72', 'Playfair Display', 'Iowan Old Style', Georgia, serif;
  --font-body:    'Avenir Next', 'Optima', -apple-system, 'Inter', system-ui, sans-serif;
  --font-mono:    ui-monospace, 'SF Mono', Menlo, monospace;

  --radius: 2px;
  --gap: 32px;
}
```

## Type

| Role | Size | Weight | Notes |
|---|---|---|---|
| Display (h1) | clamp(48px, 7vw, 104px) | 400 | high-contrast serif, line-height 1.0, tracking −0.01em |
| Section (h2) | 26–34px | 400 | serif |
| Body | 15–16px | 400 | line-height 1.7, muted |
| Label | 11px | 500 | uppercase, +0.16em — wide |

The display serif is high-contrast (thick/thin). A low-contrast serif reads as
bookish, not luxurious.

## Layout

- Container 1200px, wide gutters (48px+). Space is the product.
- One hero image or one object per screen, full-bleed.
- Sections separated by 1px hairlines at low opacity, or by 120px of space.
- The gold accent appears **once per screen**: a rule, a label, or a button.

## Component recipes

**Gold hairline label:**

```css
.kicker { font-size: 11px; letter-spacing: .16em; text-transform: uppercase;
  color: var(--accent); margin: 0 0 18px; }
```

**Ghost button:**

```css
.btn { border: 1px solid var(--border); background: transparent; color: var(--fg);
  padding: 14px 24px; border-radius: var(--radius); font-size: 13px;
  letter-spacing: .08em; text-transform: uppercase; }
.btn:hover { border-color: var(--accent); color: var(--accent); }
```

## Anti-patterns

- ❌ Pure black `#000` — use the near-black token.
- ❌ Gold on every element. Once per screen.
- ❌ A second accent colour.
- ❌ Rounded cards, gradients, glows.
- ❌ Sans-serif display type. The serif is the price signal.

## Verified example

No shipped artifact uses this grammar yet — `scripts/directions.py` can produce
it (`ember-graphite` is the nearest), and the four gates apply unchanged.

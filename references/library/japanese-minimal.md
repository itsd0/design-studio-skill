# Japanese Minimal

**Use it for:** craft products, ceramics, tea, stationery, slow software, any
product whose value is in the making.

**Why it works:** *ma* — the interval. Negative space is the material, hairline
rules are the only ornament, and one warm neutral carries the whole page.

## Tokens

```css
:root {
  --bg:        oklch(96% 0.012 85);
  --surface:   oklch(99% 0.006 85);
  --surface-2: oklch(93% 0.014 85);
  --fg:        oklch(24% 0.01 70);
  --muted:     oklch(52% 0.012 75);
  --border:    oklch(86% 0.014 80);
  --accent:    oklch(46% 0.08 35);
  --accent-on: oklch(98% 0.008 85);

  --font-display: 'Hiragino Mincho ProN', 'Yu Mincho', 'Iowan Old Style', Georgia, serif;
  --font-body:    'Hiragino Sans', 'Yu Gothic', -apple-system, 'Inter', system-ui, sans-serif;
  --font-mono:    ui-monospace, 'SF Mono', Menlo, monospace;

  --radius: 2px;
  --gap: 32px;
}
```

## Type

| Role | Size | Weight | Notes |
|---|---|---|---|
| Display (h1) | 34–52px | 400 | serif, line-height 1.35, tracking 0 |
| Section (h2) | 20–24px | 500 | line-height 1.4 |
| Body | 15–16px | 400 | line-height 1.8 — generous |
| Label | 11px | 500 | wide tracking, sentence case |

Display weight is **400**, not 700. The lightness is the point. Line-height is
generous everywhere; text is not packed.

## Layout

- One column, narrow measure (48–56ch), with wide outer margins that grow on
  larger screens: `padding-inline: clamp(24px, 12vw, 200px)`.
- Vertical rhythm comes from space, never from boxes.
- Hairlines (`1px`, low contrast) separate only what cannot be separated by
  space.
- Horizontal scroll is never used. Images are full-measure and quiet.

## Component recipes

**Interval block:**

```css
.interval { padding-block: clamp(56px, 9vw, 120px); }
.interval + .interval { border-top: 1px solid var(--border); }
```

**Quiet caption:**

```css
.caption { font-size: 11.5px; letter-spacing: .08em; color: var(--muted);
  text-transform: none; margin-top: 10px; }
```

**Link:**

```css
a { color: var(--fg); text-decoration: none; border-bottom: 1px solid var(--border); }
a:hover { border-bottom-color: var(--fg); }
```

## Anti-patterns

- ❌ Bold display type. Weight 400 is the grammar.
- ❌ Cards, borders and shadows around content.
- ❌ A saturated accent. The accent is a quiet earth tone.
- ❌ Tight line-height or dense paragraphs.
- ❌ Decorative "zen" clichés — no enso circles, no bamboo.

## Verified example

The `editorial-monocle` direction in `references/directions.md` shares the
serif-display discipline; check any artifact with `scripts/verify.py`.

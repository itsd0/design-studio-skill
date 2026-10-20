# Desert Warm

**Use it for:** travel, food, real estate, outdoor products, anything that should
feel like sunlight on a wall.

**Why it works:** sand, clay and ink. The palette is warm but not pastel, and a
serif headline against a warm ground reads as *placed* rather than generated.

## Tokens

```css
:root {
  --bg:        oklch(94% 0.03 75);
  --surface:   oklch(97% 0.02 75);
  --surface-2: oklch(89% 0.04 70);
  --fg:        oklch(28% 0.04 45);
  --muted:     oklch(50% 0.04 50);
  --border:    oklch(82% 0.05 70);
  --accent:    oklch(56% 0.14 38);
  --accent-on: oklch(97% 0.02 75);

  --font-display: 'Iowan Old Style', 'Charter', Georgia, serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'Inter', system-ui, sans-serif;
  --font-mono:    ui-monospace, 'SF Mono', Menlo, monospace;

  --radius: 10px;
  --gap: 24px;
}
```

## Type

| Role | Size | Weight | Notes |
|---|---|---|---|
| Display (h1) | 44–72px | 600 | serif, line-height 1.05, tracking −0.025em |
| Section (h2) | 28–36px | 600 | serif |
| Body | 16px | 400 | line-height 1.65 |
| Label | 11.5px | 500 | mono, uppercase, +0.08em |

Serif display, sans body. The warm ground does the rest.

## Layout

- Container 1120px, 32px gutters.
- Sections alternate between the sand ground and the lighter surface — a tonal
  rhythm, not a card rhythm.
- Images are full-bleed within a section, never floated in a card.
- Radius 10px on cards, 999px on chips. No heavy shadows.

## Component recipes

**Tonal section:**

```css
.section { padding-block: clamp(56px, 8vw, 104px); }
.section.sand { background: var(--bg); }
.section.lift { background: var(--surface); }
```

**Chip:**

```css
.chip { display: inline-flex; align-items: center; gap: 6px; border-radius: 999px;
  padding: 5px 12px; font-size: 12.5px; background: var(--surface-2);
  color: var(--fg); border: 1px solid var(--border); }
```

**Card:**

```css
.card { background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 24px; }
```

## Anti-patterns

- ❌ Cool greys anywhere. The ground is warm.
- ❌ A saturated blue accent — it fights the sand.
- ❌ Pure white surfaces.
- ❌ Pastel "beachy" clichés — no gradients, no palm silhouettes.
- ❌ More than one accent tone.

## Verified example

`assets/mobile-seed.html` uses a related warm palette; verify with
`scripts/score.py --json` to read the measured ratios.

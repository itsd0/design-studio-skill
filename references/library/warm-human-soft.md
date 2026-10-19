# Warm Human Soft

**Use it for:** health, community, education, consumer onboarding, care,
anything where a person is not a user yet.

**Why it works:** soft edges, a humanist type face and an unhurried accent
lower the temperature of a product. The layout does the work, so nothing has
to shout.

## Tokens

```css
:root {
  --bg:        oklch(97% 0.008 90);
  --surface:   oklch(99% 0.004 90);
  --surface-2: oklch(94% 0.012 90);
  --fg:        oklch(28% 0.02 50);
  --muted:     oklch(52% 0.018 55);
  --border:    oklch(89% 0.014 85);
  --accent:    oklch(58% 0.13 40);
  --accent-on: oklch(98% 0.01 90);
  --accent-soft: color-mix(in oklch, var(--accent) 12%, transparent);
  --fg-soft:     color-mix(in oklch, var(--fg) 5%, transparent);

  --font-display: 'Avenir Next', 'Optima', 'Gill Sans', 'Trebuchet MS', system-ui, sans-serif;
  --font-body:    'Avenir Next', 'Optima', 'Gill Sans', 'Trebuchet MS', system-ui, sans-serif;
  --font-mono:    ui-monospace, 'SF Mono', Menlo, monospace;

  --radius: 14px;
  --gap: 24px;
}
```

## Type

| Role | Size | Weight | Notes |
|---|---|---|---|
| Display (h1) | 40–56px | 600 | line-height 1.1, tracking −0.02em |
| Section (h2) | 28–36px | 600 | line-height 1.2 |
| Lead | 18–20px | 400 | line-height 1.6, max 54ch |
| Body | 16–17px | 400 | line-height 1.65 |
| Label | 13px | 500 | sentence case, never uppercase |

No uppercase mono labels here. This grammar speaks in sentences, not tags.

## Layout

- Container 1080px, 24px gutters. Sections breathe: 96px desktop, 64px phone.
- Content sits on a single column with a 720px measure; a second column
  appears only for real pairings (before/after, plan/actual).
- Cards are allowed here — 14px radius, `1px` border, **no shadow**. Soft
  edges, hard structure.

## Component recipes

**Soft card:**

```css
.card { background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 24px; }
.card:hover { border-color: color-mix(in oklch, var(--fg) 18%, var(--border)); }
```

**Primary button** — generous, friendly, never sharp:

```css
.btn { display: inline-flex; align-items: center; gap: 8px;
  min-height: 44px; padding: 12px 22px; border-radius: 999px;
  font-size: 15px; font-weight: 500; border: 1px solid transparent; }
.btn-primary { background: var(--accent); color: var(--accent-on); }
.btn-secondary { background: transparent; color: var(--fg); border-color: var(--border); }
```

**Step list** — replaces the icon triplet:

```css
.steps { display: grid; gap: 2px; background: var(--border);
  border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
.step { background: var(--surface); padding: 22px; display: grid;
  grid-template-columns: 40px 1fr; gap: 18px; align-items: start; }
.step .n { font-family: var(--font-mono); font-size: 12px; color: var(--accent); }
```

## Anti-patterns

- ❌ A hard grotesk display face — it reads as enterprise software.
- ❌ Uppercase tracked labels everywhere.
- ❌ Shadows on cards. Softness comes from radius and space.
- ❌ Terracotta on a cool grey ground. Warm paper, warm ink, warm accent.
- ❌ More than 44px of radius on small elements — pills and nothing else.

## Verified example

`assets/mobile-seed.html` and the `Human / Approachable` direction in
`references/directions.md` follow this grammar.

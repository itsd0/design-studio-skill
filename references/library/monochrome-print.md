# Monochrome Print

**Use it for:** newspapers, research digests, archives, documentation, anything
that should feel *printed*.

**Why it works:** newsprint grey, black ink, and hard rules. No colour at all
means hierarchy has to come from scale, weight and column structure — which is
exactly what print solved.

## Tokens

```css
:root {
  --bg:        oklch(96% 0.006 80);
  --surface:   oklch(99% 0.003 80);
  --surface-2: oklch(92% 0.008 80);
  --fg:        oklch(16% 0.005 80);
  --muted:     oklch(42% 0.008 80);
  --border:    oklch(22% 0.005 80);
  --accent:    oklch(16% 0.005 80);
  --accent-on: oklch(96% 0.006 80);

  --font-display: 'Iowan Old Style', 'Charter', Georgia, 'Times New Roman', serif;
  --font-body:    'Charter', 'Iowan Old Style', Georgia, serif;
  --font-mono:    ui-monospace, 'SF Mono', Menlo, monospace;

  --radius: 0;
  --gap: 24px;
}
```

## Type

| Role | Size | Weight | Notes |
|---|---|---|---|
| Display (h1) | 48–84px | 700 | serif, tight leading 1.02 |
| Section (h2) | 24–32px | 700 | serif |
| Body | 16–17px | 400 | serif, line-height 1.6, 62ch |
| Label | 11px | 600 | mono or sans, uppercase, +0.1em |

Both display and body are serif. That is the print voice.

## Layout

- A real multi-column grid (2–3 columns) for prose at ≥ 900px, collapsing to one.
- Hard `2px` rules above section heads; `1px` rules between items.
- Zero radius, zero shadow, zero colour except ink and paper.
- Justified text is allowed **only** with hyphenation on; otherwise left-align.

## Component recipes

**Section head:**

```css
.head { border-top: 2px solid var(--border); padding-top: 14px; margin-bottom: 24px; }
.head .kicker { font-family: var(--font-mono); font-size: 11px; letter-spacing: .1em;
  text-transform: uppercase; color: var(--muted); }
.head h2 { font-family: var(--font-display); font-size: 30px; margin: 6px 0 0; }
```

**Drop cap:**

```css
.lede::first-letter { float: left; font-family: var(--font-display); font-size: 3.4em;
  line-height: .86; padding: 4px 10px 0 0; }
```

## Anti-patterns

- ❌ Any colour. This grammar is ink and paper.
- ❌ Rounded corners or shadows.
- ❌ Justified text without hyphenation.
- ❌ Cards — use rules and columns instead.
- ❌ A sans display face. The serif is the print voice.

## Verified example

`demo/deck.html` light slides are close; `references/library/light-editorial-serif.md`
is the colour-allowed sibling.

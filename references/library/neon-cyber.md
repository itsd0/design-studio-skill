# Neon Cyber

**Use it for:** games, music tools, creative software, events, anything with a
stage and a crowd.

**Why it works:** near-black plus two electric hues, used as *light* rather than
fill. The constraint is that the neon never carries body copy.

## Tokens

```css
:root {
  --bg:        oklch(10% 0.02 285);
  --surface:   oklch(14% 0.03 285);
  --surface-2: oklch(19% 0.04 285);
  --fg:        oklch(95% 0.01 285);
  --muted:     oklch(68% 0.03 285);
  --border:    oklch(30% 0.06 285);
  --accent:    oklch(78% 0.24 330);
  --accent-on: oklch(12% 0.03 285);
  --cyan:      oklch(82% 0.16 195);

  --font-display: 'Avenir Next', 'Century Gothic', Futura, system-ui, sans-serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'Inter', system-ui, sans-serif;
  --font-mono:    ui-monospace, 'SF Mono', Menlo, monospace;

  --radius: 8px;
  --gap: 24px;
}
```

## Type

| Role | Size | Weight | Notes |
|---|---|---|---|
| Display (h1) | clamp(44px, 8vw, 110px) | 700 | tracking −0.03em, line-height 0.96 |
| Section (h2) | 26–36px | 600 | |
| Body | 15–16px | 400 | line-height 1.65, `--fg` — never neon |
| Label | 11px | 500 | mono, uppercase, +0.12em |

Neon is for **display, rules, icons, and one CTA**. Body copy is always `--fg`.

## Layout

- Container 1200px, 32px gutters, dark.
- Diagonal or offset composition is allowed once per page — one grid-break.
- Thin neon rules (1px) as section dividers; no filled neon blocks behind text.
- Images are dark-treated or omitted; the type is the visual.

## Component recipes

**Neon rule:**

```css
.neon-rule { height: 1px; border: 0; margin: 0 0 24px;
  background: linear-gradient(90deg, var(--accent), transparent); }
```

**Glow CTA** (one per page):

```css
.btn-primary { background: var(--accent); color: var(--accent-on);
  border-radius: var(--radius); padding: 13px 24px; font-weight: 700;
  box-shadow: 0 0 24px color-mix(in oklch, var(--accent) 45%, transparent); }
```

## Anti-patterns

- ❌ Neon body text. Contrast and legibility fail immediately.
- ❌ Two glows competing in one viewport.
- ❌ Purple→pink gradient text — that is the AI-slop tell, not this grammar.
- ❌ Saturated fills behind paragraphs.
- ❌ More than two electric hues.

## Verified example

No shipped artifact uses this grammar; `scripts/verify.py` will flag glow-driven
contrast problems, so measure before shipping.

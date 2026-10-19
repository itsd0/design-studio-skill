# Cinematic Ember

**Use it for:** studios, agencies, premium launches, portfolios, anything that
should feel like a title card rather than a website.

**Why it works:** near-black, one ember accent, and a display size large enough
that the layout disappears. Restraint is the whole style.

## Tokens

```css
:root {
  --bg:        oklch(15% 0.004 250);
  --surface:   oklch(19% 0.005 250);
  --surface-2: oklch(24% 0.006 250);
  --fg:        oklch(95% 0.003 250);
  --muted:     oklch(66% 0.008 250);
  --border:    oklch(30% 0.007 250);
  --accent:    oklch(66% 0.19 40);
  --accent-on: oklch(15% 0.01 40);
  --accent-soft: color-mix(in oklch, var(--accent) 16%, transparent);
  --fg-soft:     color-mix(in oklch, var(--fg) 6%, transparent);

  --font-display: 'Avenir Next', 'Century Gothic', Futura, system-ui, sans-serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'Inter', system-ui, sans-serif;
  --font-mono:    ui-monospace, 'SF Mono', Menlo, monospace;

  --radius: 2px;
  --gap: 28px;
}
```

## Type

| Role | Size | Notes |
|---|---|---|
| Display (h1) | clamp(56px, 9vw, 132px) | weight 600, line-height 0.96, tracking −0.04em |
| Section (h2) | 30–44px | weight 600, tracking −0.03em |
| Lead | 17–19px | muted, max 52ch |
| Body | 15–16px | line-height 1.6 |
| Label | 11px | mono, uppercase, +0.1em, muted |

The display size is the design. If the h1 is under 56px, the grammar is not
this grammar.

## Layout

- Container 1240px, 32px gutters.
- One statement per screen. Full-height sections, `100vh`, one claim each.
- Generous negative space: sections at 140px, and the hero at 1.2 viewports.
- Grid breaks are the punctuation — one overlapping element per two screens.

## Component recipes

**Full-bleed statement:**

```css
.statement { min-height: 100vh; display: grid; align-content: center;
  padding-block: clamp(80px, 12vh, 160px); }
.statement h1 { font-family: var(--font-display); font-weight: 600;
  font-size: clamp(56px, 9vw, 132px); line-height: .96; letter-spacing: -.04em;
  margin: 0; max-width: 14ch; }
```

**Ember rule** — the one place the accent draws:

```css
.ember-rule { width: 64px; height: 2px; background: var(--accent);
  border: 0; margin: 0 0 28px; }
```

**Work index** — a list, not a card grid:

```css
.index { border-top: 1px solid var(--border); }
.index-item { display: grid; grid-template-columns: 72px 1fr auto; gap: 24px;
  align-items: baseline; padding: 26px 0; border-bottom: 1px solid var(--border);
  transition: color .15s ease; }
.index-item:hover { color: var(--accent); }
.index-item .n { font-family: var(--font-mono); font-size: 12px; color: var(--muted); }
```

## Anti-patterns

- ❌ A hero under 56px. The scale is the identity.
- ❌ A second accent colour. Ember or nothing.
- ❌ Drop shadows, glassmorphism, gradients. The ground is flat black.
- ❌ Three cards of equal weight. One thing is the work.
- ❌ A dark UI with a light-mode fallback that was never designed.

## Verified example

The `Ember Graphite` direction in `references/directions.md` and the
`demo/deck.html` dark slides follow this grammar.

# Dark Structural Grid

**Use it for:** developer tools, AI infrastructure, agent runtimes, observability
dashboards, anything where a human is watching a machine work.

**Why it works:** the structure is the decoration. Nothing floats; a `1px`
hairline grid carries the layout, so the only colour on screen is the one
signal the product exists to show.

## Tokens

```css
:root {
  --bg:        oklch(13% 0.006 255);
  --surface:   oklch(16% 0.008 255);
  --surface-2: oklch(20% 0.010 255);
  --fg:        oklch(96% 0.004 255);
  --muted:     oklch(68% 0.012 255);
  --border:    oklch(24% 0.010 255);
  --accent:    oklch(80% 0.17 152);
  --accent-on: oklch(15% 0.02 152);
  --accent-soft: color-mix(in oklch, var(--accent) 14%, transparent);
  --fg-soft:     color-mix(in oklch, var(--fg) 6%, transparent);

  --font-display: -apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', system-ui, sans-serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Text', system-ui, sans-serif;
  --font-mono:    'JetBrains Mono', 'Geist Mono', 'IBM Plex Mono', ui-monospace, Menlo, monospace;

  --radius: 6px;
  --gap: 20px;
}
```

## Type

| Role | Size | Weight | Tracking |
|---|---|---|---|
| Display (h1) | 44–72px | 600 | −0.028em |
| Section (h2) | 30–44px | 600 | −0.02em |
| Lead | 17–20px | 400 | −0.01em |
| Body | 15–16px | 400 | 0 |
| Label (mono, uppercase) | 11–12px | 500 | +0.07em |

Numbers are mono with `font-variant-numeric: tabular-nums`. Uppercase mono
labels carry the technical voice; never set body copy in mono.

## Layout

- Container 1180px, 32px gutters.
- Sections separated by `1px solid var(--border)`, never by a colour change.
- Bento grids are **gapless**: `gap: 1px; background: var(--border)` with
  `1px` borders on the cells, so the grid reads as structure.
- One grid-break per page — the hero stage, an overlapping spec row, or a
  full-bleed panel. One.

## Component recipes

**Studio window** (the product stage — use it for any real UI preview):

```html
<div class="app-window">
  <div class="app-bar">
    <span class="win-dots" aria-hidden="true"><i></i><i></i><i></i></span>
    <span>service · session</span>
    <span class="win-tabs"><span class="win-tab active"># trace.canvas</span></span>
  </div>
  <div class="app-panes">…</div>
</div>
```

```css
.app-window { background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; overflow: hidden; }
.app-bar { display: flex; align-items: center; justify-content: space-between;
  gap: 16px; padding: 10px 16px; border-bottom: 1px solid var(--border);
  background: var(--bg); font-family: var(--font-mono); font-size: 12px;
  color: var(--muted); flex-wrap: wrap; }
.app-panes { display: grid; grid-template-columns: 235px 1fr 1.2fr; gap: 1px;
  background: var(--border); min-height: 330px; }
@media (max-width: 920px) { .app-panes { grid-template-columns: minmax(0, 1fr); } }
```

**Bento cell** — a hairline cell with a schematic, never an icon:

```css
.bento-hairline { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1px; background: var(--border); border: 1px solid var(--border);
  border-radius: 12px; overflow: hidden; }
.bento-cell { background: var(--surface); padding: 20px; }
```

## Anti-patterns

- ❌ Purple/indigo accents, or a gradient anywhere.
- ❌ Floating cards with `box-shadow` where a hairline grid belongs.
- ❌ White text on a luminous accent — use `--accent-on`.
- ❌ More than one signal colour, or the accent on more than two elements.
- ❌ A text-only hero. Anchor it with the studio window.
- ❌ Emoji as icons. Use inline SVG.

## Verified example

`demo/landing.html` ships this grammar end to end and passes
`scripts/lint.py`, `scripts/verify.py` and `scripts/score.py` clean.

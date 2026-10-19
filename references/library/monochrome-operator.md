# Monochrome Operator

**Use it for:** terminals, CLIs, log viewers, admin consoles, infrastructure
panels — anything whose audience reads more than it looks.

**Why it works:** the interface is mostly text, so the design work moves to
the *rhythm* of the text and the one amber signal that means something is
wrong.

## Tokens

```css
:root {
  --bg:        oklch(12% 0.012 70);
  --surface:   oklch(16% 0.014 70);
  --surface-2: oklch(21% 0.016 70);
  --fg:        oklch(94% 0.02 90);
  --muted:     oklch(66% 0.02 80);
  --border:    oklch(27% 0.02 75);
  --accent:    oklch(82% 0.15 85);
  --accent-on: oklch(15% 0.02 70);
  --accent-soft: color-mix(in oklch, var(--accent) 14%, transparent);
  --fg-soft:     color-mix(in oklch, var(--fg) 7%, transparent);

  --font-display: ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, monospace;
  --font-body:    ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, monospace;
  --font-mono:    ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, monospace;

  --radius: 2px;
  --gap: 16px;
}
```

## Type

| Role | Size | Notes |
|---|---|---|
| Display (h1) | 30–40px | mono, weight 600, tracking −0.01em |
| Section (h2) | 18–22px | mono, uppercase, +0.08em |
| Body | 13–14px | mono, line-height 1.5 |
| Data | 12–13px | mono, `tabular-nums` |

Everything is mono. That is the constraint that makes the layout legible: with
one family, hierarchy comes from size, weight and colour alone.

## Layout

- Container 1100px, 24px gutters. Density is **compact** — 48px sections.
- A status bar on top: product, version, environment, connection state.
- Rows are `1px` separated, never carded. A list of rows is a table.
- The command line is the hero. A prompt is the primary call to action.

## Component recipes

**Prompt bar** — the hero of this grammar:

```css
.prompt { display: flex; align-items: center; gap: 10px;
  border: 1px solid var(--border); background: var(--surface);
  border-radius: var(--radius); padding: 12px 14px;
  font-family: var(--font-mono); font-size: 13px; }
.prompt::before { content: '$'; color: var(--accent); }
```

**Log rows:**

```css
.log-row { display: grid; grid-template-columns: 72px 1fr auto; gap: 14px;
  padding: 7px 0; border-bottom: 1px solid var(--border); font-size: 12.5px; }
.log-row .ts { color: var(--muted); }
.log-row .level { color: var(--accent); }
```

**Status pill** — the only place colour is allowed to carry meaning:

```css
.pill { display: inline-flex; align-items: center; gap: 6px;
  font-family: var(--font-mono); font-size: 11px; letter-spacing: .06em;
  text-transform: uppercase; padding: 3px 8px; border-radius: 999px;
  border: 1px solid var(--border); color: var(--muted); }
.pill.ok { color: var(--accent); border-color: var(--accent); }
```

## Anti-patterns

- ❌ A grotesk sneaking into the display face. Mono all the way down.
- ❌ Rounded corners above 4px. This is a machine interface.
- ❌ Colour used decoratively — amber means *signal*, nothing else.
- ❌ A marketing hero with a centred headline. The prompt is the hero.
- ❌ Emoji in a status line. Use a glyph or a shape.

## Verified example

`assets/deck-seed.html` and `assets/agent-seed.html` carry the operator
grammar in their chrome, and both pass the three gates.

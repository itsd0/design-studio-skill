# Pastel Playful

**Use it for:** consumer apps, kids' products, learning tools, community
platforms — anywhere delight is part of the job.

**Why it works:** soft fields of colour, large rounded shapes, and one dark ink
keep playfulness from turning into noise. The contrast rules still apply.

## Tokens

```css
:root {
  --bg:        oklch(98% 0.008 320);
  --surface:   oklch(100% 0 0);
  --surface-2: oklch(95% 0.03 320);
  --fg:        oklch(25% 0.02 300);
  --muted:     oklch(50% 0.03 300);
  --border:    oklch(90% 0.02 320);
  --accent:    oklch(58% 0.16 330);
  --accent-on: oklch(99% 0.004 320);
  --mint:      oklch(90% 0.07 165);
  --butter:    oklch(94% 0.09 95);
  --lilac:     oklch(88% 0.06 300);

  --font-display: 'Avenir Next', 'Century Gothic', 'Trebuchet MS', system-ui, sans-serif;
  --font-body:    'Avenir Next', 'Century Gothic', 'Trebuchet MS', system-ui, sans-serif;
  --font-mono:    ui-monospace, 'SF Mono', Menlo, monospace;

  --radius: 20px;
  --gap: 20px;
}
```

## Type

| Role | Size | Weight | Notes |
|---|---|---|---|
| Display (h1) | clamp(36px, 5vw, 60px) | 700 | line-height 1.08, tracking −0.02em |
| Section (h2) | 24–30px | 600 | |
| Body | 16–17px | 400 | line-height 1.62 |
| Label | 13px | 600 | sentence case |

Rounded sans only. A serif reads as "serious brand" and breaks the tone.

## Layout

- Container 1080px, 24px gutters.
- Large rounded blocks (20–28px) with generous internal padding.
- Pastel fields are **backgrounds**, not borders: a mint panel behind a real
  block, never a thin pastel outline.
- One dark ink for all text. Pastel text on white fails contrast — verify it.

## Component recipes

**Pastel panel:**

```css
.panel { background: var(--mint); border-radius: 24px; padding: 32px; }
.panel.butter { background: var(--butter); }
.panel.lilac { background: var(--lilac); }
```

**Rounded button:**

```css
.btn { border-radius: 999px; padding: 13px 24px; font-weight: 700; font-size: 15px;
  border: 0; background: var(--accent); color: var(--accent-on); }
.btn-secondary { background: var(--surface); color: var(--fg); border: 2px solid var(--border); }
```

## Anti-patterns

- ❌ Pastel text on a pastel field — check contrast, always.
- ❌ More than three pastel fields per screen.
- ❌ Sharp corners, hairline tables, or mono body copy.
- ❌ Emoji as the only icon system.
- ❌ Gradients — the fields are flat.

## Verified example

`assets/mobile-seed.html` has a related warm/soft palette; the contrast gate will
catch pastel-on-pastel immediately. Run `scripts/verify.py`.

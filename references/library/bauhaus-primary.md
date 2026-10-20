# Bauhaus Primary

**Use it for:** education, creative tools, children's products, brand systems
that want to feel constructed rather than styled.

**Why it works:** primary colours, geometric primitives, and a heavy grotesk
make the page read as *built*. Shapes carry the composition so photography is
optional.

## Tokens

```css
:root {
  --bg:        oklch(97% 0.012 95);
  --surface:   oklch(100% 0 0);
  --surface-2: oklch(93% 0.02 95);
  --fg:        oklch(18% 0.01 250);
  --muted:     oklch(46% 0.02 250);
  --border:    oklch(18% 0.01 250);
  --accent:    oklch(55% 0.22 27);
  --accent-on: oklch(99% 0 0);
  --blue:      oklch(52% 0.19 255);
  --yellow:    oklch(88% 0.17 95);

  --font-display: 'Avenir Next', 'Century Gothic', Futura, system-ui, sans-serif;
  --font-body:    'Avenir Next', 'Century Gothic', Futura, system-ui, sans-serif;
  --font-mono:    ui-monospace, 'SF Mono', Menlo, monospace;

  --radius: 999px;
  --gap: 24px;
}
```

## Type

| Role | Size | Weight | Notes |
|---|---|---|---|
| Display (h1) | clamp(44px, 7vw, 96px) | 700 | line-height 1.0, tracking −0.02em |
| Section (h2) | 26–34px | 700 | |
| Body | 16px | 400 | line-height 1.6 |
| Label | 12px | 600 | uppercase, +0.06em |

Geometric sans only. If the display face is a serif or a neutral grotesk, the
grammar collapses.

## Layout

- A 3×3 or 4×4 visible module grid; shapes snap to the modules.
- Circles, half-circles, triangles and bars as *composition*, not decoration —
  each shape must anchor a real content block.
- Radius 999px on buttons and tags; 0 on panels. The contrast is deliberate.
- Keep one large shape per screen. Three competing circles is noise.

## Component recipes

**Shape-anchored feature:**

```css
.feature { display: grid; grid-template-columns: 120px 1fr; gap: 24px;
  align-items: start; padding: 28px 0; border-top: 2px solid var(--border); }
.feature .shape { width: 96px; height: 96px; border-radius: 999px;
  background: var(--blue); }
.feature .shape.square { border-radius: 0; background: var(--accent); }
.feature .shape.triangle { width: 0; height: 0; background: none;
  border-left: 48px solid transparent; border-right: 48px solid transparent;
  border-bottom: 84px solid var(--yellow); border-radius: 0; }
```

**Pill button:**

```css
.btn { border-radius: 999px; padding: 12px 22px; font-weight: 600;
  border: 2px solid var(--border); background: var(--surface); color: var(--fg); }
.btn-primary { background: var(--accent); border-color: var(--accent); color: var(--accent-on); }
```

## Anti-patterns

- ❌ Pastel primaries. The colours are primaries, at full strength.
- ❌ Shapes without a content job.
- ❌ Drop shadows or gradients — the composition is flat.
- ❌ A neutral corporate grotesk as the display face.
- ❌ More than three colours plus ink and paper.

## Verified example

The `brutalist-experimental` direction in `references/directions.md` shares this
palette logic; verify any artifact with `scripts/score.py`.

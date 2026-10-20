# Swiss Poster

**Use it for:** cultural products, conferences, architecture practices, anything
with a point of view and no patience for decoration.

**Why it works:** International Typographic Style. Asymmetric grid, one grotesk,
red on white, and type large enough to be the image. The discipline is the
style.

## Tokens

```css
:root {
  --bg:        oklch(99% 0 0);
  --surface:   oklch(96% 0 0);
  --surface-2: oklch(92% 0 0);
  --fg:        oklch(15% 0 0);
  --muted:     oklch(45% 0 0);
  --border:    oklch(20% 0 0);
  --accent:    oklch(52% 0.22 27);
  --accent-on: oklch(99% 0 0);
  --fg-soft:   color-mix(in oklch, var(--fg) 6%, transparent);

  --font-display: 'Helvetica Neue', Helvetica, 'Inter', Arial, sans-serif;
  --font-body:    'Helvetica Neue', Helvetica, 'Inter', Arial, sans-serif;
  --font-mono:    ui-monospace, 'SF Mono', Menlo, monospace;

  --radius: 0;
  --gap: 20px;
}
```

## Type

| Role | Size | Weight | Notes |
|---|---|---|---|
| Display (h1) | clamp(56px, 10vw, 160px) | 700 | line-height 0.9, tracking −0.04em |
| Section (h2) | 28–40px | 700 | tracking −0.02em |
| Body | 15–16px | 400 | line-height 1.45, measure 58ch |
| Label | 11–12px | 500 | uppercase, +0.08em |

No italics, no second family. One weight jump is enough.

## Layout

- **Asymmetric.** A 12-column grid where content occupies 1–7 and 8–12, never
  centred. The empty column is part of the composition.
- Hard rules: `1px solid var(--fg)` for section breaks, `3px` for the accent.
- Radius 0 everywhere. Buttons are rectangles.
- Alignment is the design: every element snaps to the same left edge or the
  same baseline.

## Component recipes

**Poster headline block:**

```css
.poster { display: grid; grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: var(--gap); align-items: end; padding-block: clamp(48px, 8vw, 96px); }
.poster h1 { grid-column: 1 / span 9; font-family: var(--font-display);
  font-size: clamp(56px, 10vw, 160px); line-height: .9; letter-spacing: -.04em;
  font-weight: 700; margin: 0; text-wrap: balance; }
.poster .meta { grid-column: 10 / span 3; font-size: 13px; line-height: 1.4; }
```

**Red rule + index:**

```css
.rule-accent { height: 3px; background: var(--accent); border: 0; margin: 0 0 20px; }
.index-row { display: grid; grid-template-columns: 64px 1fr auto; gap: 20px;
  padding: 14px 0; border-bottom: 1px solid var(--border); align-items: baseline; }
```

**Button:**

```css
.btn { border-radius: 0; padding: 12px 20px; font-weight: 600; font-size: 14px;
  border: 1px solid var(--fg); background: transparent; color: var(--fg); }
.btn-primary { background: var(--accent); border-color: var(--accent); color: var(--accent-on); }
```

## Anti-patterns

- ❌ Centred hero copy. The asymmetry is the identity.
- ❌ Rounded corners or shadows.
- ❌ More than one accent colour, or the red used for decoration.
- ❌ A second type family.
- ❌ Illustration. Type and rules are the imagery.

## Verified example

`assets/prototype-seed.html` in its `brutalist-experimental` configuration
carries this grammar; run the four gates on any artifact that claims it.

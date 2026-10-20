# Civic Blue

**Use it for:** public services, healthcare portals, education platforms,
utilities, anything where trust is the first requirement.

**Why it works:** a calm institutional blue, generous type, and a layout that
looks like it was tested with real people. Accessibility is not a feature here;
it is the design.

## Tokens

```css
:root {
  --bg:        oklch(99% 0.003 240);
  --surface:   oklch(100% 0 0);
  --surface-2: oklch(95% 0.012 240);
  --fg:        oklch(22% 0.03 250);
  --muted:     oklch(48% 0.03 250);
  --border:    oklch(88% 0.02 245);
  --accent:    oklch(45% 0.15 255);
  --accent-on: oklch(99% 0 0);
  --success:   oklch(48% 0.12 150);
  --danger:    oklch(50% 0.18 25);

  --font-display: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', system-ui, sans-serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', system-ui, sans-serif;
  --font-mono:    ui-monospace, 'SF Mono', Menlo, monospace;

  --radius: 6px;
  --gap: 20px;
}
```

## Type

| Role | Size | Weight | Notes |
|---|---|---|---|
| Display (h1) | 32–44px | 700 | line-height 1.15 |
| Section (h2) | 22–26px | 600 | |
| Body | 16–17px | 400 | line-height 1.6 — never smaller |
| Label | 14px | 600 | sentence case, visible |

Body text is **16px minimum**. Public-service interfaces do not get to use
13px body copy.

## Layout

- Container 1080px, 24px gutters.
- One column for prose, two for form + help.
- Every form field has a visible label above it, a hint, and an error slot.
- Skip link, landmarks, and a visible focus ring on every control.
- Tables scroll inside their own box; they never push the page sideways.

## Component recipes

**Field with label + hint + error:**

```css
.field { display: grid; gap: 6px; }
.field label { font-weight: 600; font-size: 15px; }
.field .hint { color: var(--muted); font-size: 14px; }
.field input { min-height: 44px; padding: 10px 12px; font: inherit;
  border: 1px solid var(--border); border-radius: var(--radius); background: var(--surface); }
.field input:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }
.field .error { color: var(--danger); font-size: 14px; }
```

**Notice:**

```css
.notice { border-left: 4px solid var(--accent); background: var(--surface-2);
  padding: 16px 18px; border-radius: 0 var(--radius) var(--radius) 0; }
```

## Anti-patterns

- ❌ Body text under 16px.
- ❌ Placeholder-as-label. Ever.
- ❌ Colour as the only signal — pair every state with text or an icon.
- ❌ Decorative hero images on a task page.
- ❌ Auto-focus, auto-advance, or a carousel.

## Verified example

The `tech-utility` direction in `references/directions.md` is the closest shipped
grammar; run `scripts/verify.py` to confirm tap targets and contrast.

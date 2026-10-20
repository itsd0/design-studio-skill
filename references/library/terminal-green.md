# Terminal Green

**Use it for:** security tooling, hacking-adjacent products, developer demos,
anything that wants a CRT on the desk.

**Why it works:** phosphor green on near-black is a *reference*, not a palette.
Used with restraint it signals "machine" faster than any icon.

## Tokens

```css
:root {
  --bg:        oklch(10% 0.01 150);
  --surface:   oklch(14% 0.012 150);
  --surface-2: oklch(18% 0.014 150);
  --fg:        oklch(88% 0.14 145);
  --muted:     oklch(62% 0.09 145);
  --border:    oklch(28% 0.04 150);
  --accent:    oklch(85% 0.21 145);
  --accent-on: oklch(12% 0.02 150);

  --font-display: ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, monospace;
  --font-body:    -apple-system, BlinkMacSystemFont, 'Inter', system-ui, sans-serif;
  --font-mono:    ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, monospace;

  --radius: 0;
  --gap: 16px;
}
```

## Type

| Role | Size | Notes |
|---|---|---|
| Display (h1) | 26–36px | mono, weight 500, tracking −0.01em |
| Section (h2) | 15–18px | mono, uppercase, +0.08em |
| Body | 13–14px | sans, line-height 1.6 — readable at length |
| Data | 12–13px | mono, `tabular-nums` |

Mono for the *machine voice* (headings, data, labels); sans for the *human
voice* (body paragraphs). Switching between them is the hierarchy.

## Layout

- Container 1100px, 20px gutters. Compact.
- Everything sits on a 4px baseline; rows are `1px` separated.
- A scanline or dot-grid background is allowed at ≤ 3% opacity — never more.
- No rounded corners. No shadows. The screen is flat.

## Component recipes

**Terminal block:**

```css
.term { background: var(--bg); border: 1px solid var(--border);
  padding: 16px 18px; font-family: var(--font-mono); font-size: 12.5px;
  line-height: 1.7; overflow-x: auto; }
.term .prompt { color: var(--accent); }
.term .dim { color: var(--muted); }
```

**Status line:**

```css
.status { display: flex; gap: 18px; flex-wrap: wrap; font-family: var(--font-mono);
  font-size: 11.5px; color: var(--muted); border-top: 1px solid var(--border);
  padding-top: 12px; }
.status .ok { color: var(--accent); }
```

## Anti-patterns

- ❌ Saturated green body text at length. Body copy is light, not phosphor.
- ❌ Glow effects and text-shadow on everything. One glow, at most.
- ❌ Emoji or ASCII art as decoration.
- ❌ Rounded corners. This is a terminal.
- ❌ A second accent (amber is a *different* grammar — pick one).

## Verified example

`references/library/monochrome-operator.md` is the amber sibling; choose one per
product, never both. Verify with `scripts/verify.py` for contrast on the green.

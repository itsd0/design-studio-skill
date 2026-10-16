# Ferry

> Category: Developer tools / local-first utilities
> File transfer between a person's own machines. Direct, resumable, no accounts.

## Visual Theme & Atmosphere
Utility first, quiet chrome. Data is the decoration: command output, file states, transfer progress. Nothing floats, nothing glows — hairline borders and whitespace carry the layout.

## Color Palette & Roles
- **Background:** `oklch(98% 0.005 250)`
- **Foreground:** `oklch(22% 0.02 240)` — body and headings; never pure black
- **Accent:** `oklch(58% 0.16 145)` — signal green: primary CTA, eyebrow labels, transfer-confirmed marks; at most 2 visible uses per screen
- **Muted:** `oklch(50% 0.018 240)` — secondary text, captions
- **Border:** `oklch(90% 0.008 240)` — hairlines only
- **Surface:** `oklch(100% 0 0)` — terminal cards, tables
- No separate status palette; success is the accent, warnings use plain foreground.
- Anti-patterns: never pure black; never pure white page backgrounds; no gradients except the muted placeholder texture.

## Typography Rules
- **Display / headings:** `-apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', system-ui, sans-serif`, weight 600 — one sans family for display and body is correct for this direction
- **Body:** same stack, weight 400
- **Mono:** `'JetBrains Mono', 'IBM Plex Mono', ui-monospace, Menlo, monospace` — commands, paths, hashes, IDs
- Scale (px): 12 · 13 · 16 · 19 · 22 · 32–48 · 44–76 (clamped)
- Line-height: 1.55 body, 1.04–1.1 headings
- Letter-spacing: -0.02em on display sizes ≥32px; +0.06em minimum on any uppercase label
- Tabular numerics (`font-variant-numeric: tabular-nums`) wherever numbers can line up

## Component Stylings
- **Buttons:** 10px radius, 11×20px padding; primary = accent fill; secondary = transparent with hairline border; no shadows
- **Cards / terminal:** surface fill, 1px border, 16px radius, no shadow
- **Tables:** hairline row rules, mono uppercase headers with 0.06em tracking, no zebra stripes
- **Links:** foreground color; hover to accent only when the screen has accent budget left

## Layout Principles
- Container 1120px, 32px gutters; 8-point spacing grid
- Hero: centered, generous (80–160px block padding), no illustration — the headline and the command are the hero
- Sections separated by 1px rules; whitespace first
- Desktop ≥ 1024px: full grid · tablet/phone ≤ 920px: single column, no fixed widths

## Depth & Elevation
Flat (0) only. Hairline borders instead of shadows; no glassmorphism; no decorative gradients.

## Do's and Don'ts
- ✅ Show the product: terminal transcripts, file counts, states
- ✅ One accent moment per section — a CTA or a confirmation, never both
- ❌ No hero images, no oversized marketing claims, no numbers without a source
- ❌ No shadows, no avatars, no emoji

## Responsive Behavior
- **Desktop ≥ 1024px:** full container, split layouts allowed
- **Tablet 640–1023px:** grids collapse to 2-up where sensible
- **Phone < 640px:** single column; the terminal scrolls horizontally inside its card

## Agent Prompt Guide
- When in doubt, subtract: fewer colors, fewer words, fewer borders.
- Accent budget: 2 per screen; state where it is spent before every build.
- Token discipline: no hex values outside `:root`; derive tones with `color-mix()` only.
- Copy rules: concrete nouns, no adjectives that could describe any product.

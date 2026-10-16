# [Brand Name]

> Category: [e.g. Starter / Productivity & SaaS / Editorial]
> [One sentence: what this brand is and when to use it.]

## Visual Theme & Atmosphere
[2–3 concrete sentences of mood. "Calm, functional, quietly confident. No ornament. Content-first, chrome-second." — not vibes.]

## Color Palette & Roles
- **Background:** `[#value]`
- **Foreground:** `[#value]`
- **Accent:** `[#value]` — [primary CTAs, links, one hero element per screen]
- **Muted:** `[#value]` — [secondary text, captions]
- **Border:** `[#value]`
- **Surface:** `[#value]` — [cards, modals]
- **Success:** `[#value]`, **Warn:** `[#value]`, **Danger:** `[#value]`
[State the anti-patterns: "Never pure black; never pure white for backgrounds."]

## Typography Rules
- **Display / headings:** `[stack]`, weight [600]
- **Body:** `[stack]`, weight [400]
- **Mono:** `[stack]`
- Scale (px): [12 · 14 · 16 · 20 · 24 · 32 · 48 · 64]
- Line-height: [1.5] body, [1.2] headings
- Letter-spacing: [-0.01em] on display sizes ≥32px
- [CJK note if the artifact may render CJK: display leading 1.3–1.4, tracking 0]

## Component Stylings
- **Buttons:** [radius, padding, primary fill, secondary border, states]
- **Cards:** [surface, border, radius, padding, shadow policy]
- **Inputs:** [border, radius, padding, focus treatment]
- **Links:** [color, underline policy]

## Layout Principles
- [Grid: 12-column, max-width, gutters]
- [Hero height and bias]
- [Section spacing per breakpoint: desktop / tablet / phone]
- [Separator policy: whitespace first, dividers only between unrelated sections]

## Depth & Elevation
[Named levels only — e.g. Flat (0) default; Raised (1) dropdowns/modals/floating buttons with the exact shadow recipe. "No neumorphism, no glassmorphism."]

## Do's and Don'ts
- ✅ [Let whitespace do the work.]
- ✅ [One accent element per screen.]
- ❌ [No gradients / no shadows on inputs / no more than three type sizes on one screen.]

## Responsive Behavior
- **Desktop ≥ 1024px:** [12-col grid, gutters]
- **Tablet 640–1023px:** [8-col grid, gutters]
- **Phone < 640px:** [4-col grid, gutters; hero changes]

## Agent Prompt Guide
- [The tiebreaker rules for ambiguous cases. E.g. "When in doubt, subtract."]
- [Accent budget statement.]
- [Token discipline: "Do not invent hex values outside this palette. If the request needs one, use the closest existing token and surface a warning comment."]

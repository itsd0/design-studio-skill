# Quality gates — craft rules and the review checklist

Universal rules that apply on top of any DESIGN.md. The design system decides *which* values; this file decides *how* they behave. P0 = must pass before delivery; P1 = should pass; P2 = nice to have. `scripts/lint.py` auto-checks the mechanical half — run it early and often.

## The seven cardinal sins (P0, auto-checked by `scripts/lint.py`)

1. **Default LLM indigo as accent** — hardcoded `#6366f1`, `#4f46e5`, `#4338ca`, `#3730a3`, `#8b5cf6`, `#7c3aed`, `#a855f7` (anywhere outside a token block that legitimately defines `--accent`). Use `var(--accent)`.
2. **Two-stop "trust" gradient on a hero** — purple→blue, blue→cyan, indigo→pink. A flat surface + intentional type beats it every time.
3. **Emoji as feature/UI icons** — `✨🚀🎯⚡🔥💡📈🎨🛡️🌟💪🎉👋🙌✅⭐🏆` inside headings, buttons, list items, icon classes. Use 1.6–1.8px-stroke monoline SVG with `currentColor`.
4. **Sans-serif display face when the seed binds a serif** — h1/h2 must use `var(--font-display)`, never a hardcoded Inter / Roboto / Arial / `system-ui`.
5. **Rounded card with a colored left-border accent** — the canonical "AI dashboard tile". Drop either the radius or the left border.
6. **Invented metrics** — "10× faster", "99.9% uptime", "3× more productive". Use real sources or labeled placeholders.
7. **Filler copy** — lorem ipsum, "Feature One / Two / Three", "placeholder text". An empty section is a composition problem, not a copy problem.

## Soft tells (P1)

- Stock "Hero → Features → Pricing → FAQ → CTA" with no variation — introduce one unconventional section (full-bleed quote wall, pricing as comparison-against-status-quo, inline mini-demo).
- External placeholder image CDNs (unsplash, placehold.co, picsum, placekitten).
- More than ~12 raw hex values outside `:root`.
- `var(--accent)` used 6+ times inline in the rendered body.

## Calibrating the three cliché looks

These are the looks an agent drifts toward when it hasn't committed to a direction. Recognize them; ship one only if the brief *explicitly* asks for it — and then with every craft budget in this file intact.

1. **The pastel SaaS.** Indigo→violet gradient hero, two rounded ghost buttons, three identical feature cards, Inter everywhere, glassmorphism nav, a "Trusted by" row of blank gray logo slabs.
2. **The dark-mode dev tool.** Near-black background, neon green/cyan glow accents, monospace headlines, terminal typing animation, grid overlay, fake log lines.
3. **The beige editorial clone.** Warm paper background, high-contrast serif display, faux-justified prose, an italic accent in every heading, film grain overlay, drop caps.

The cure is never "add more style" — it's going back to the brief and asking what only *this* product would do.

## Typography

- **Scale:** multiplicative (1.2 / 1.25), 6–8 sizes max per artifact. Display 48–72 · H1 32–48 · H2 24–32 · H3 20–24 · body 15–18 · small 13–14 · caption 11–12.
- **Leading:** display/H1 ≥32px → 1.0–1.2 (tight); body → 1.5–1.6; small → 1.5.
- **CJK overrides (not optional):** CJK glyphs fill the em box — display leading 1.3–1.4, body 1.7–1.8. Negative tracking is Latin-only; CJK display gets `0`. Applies to the cover/hero title at any size, including multi-line `<br>` splits.
- **Letter-spacing:** body `0` · small text `+0.01–0.02em` · UI labels/buttons `+0.02em` · **ALL CAPS `+0.06–0.1em` (required)** · headings 32px+ `−0.01–0.02em` · display 48px+ `−0.02–0.03em`. The two most reliable AI tells are ALL-CAPS without tracking and display text without negative tracking.
- **Pairs:** max 2 typefaces per artifact, always with a system fallback. Never `font-family: system-ui` alone on a heading.
- **Line length:** 50–75 characters (`max-width: 65ch` is a safe default; 60ch in seeds).
- **Weights:** exactly 3 — read (400/450), emphasize (510/550), announce (590/600). 700+ is rarely needed.
- **Above the fold:** no more than 3 type sizes visible. Never `text-align: justify` on the web (lint P1).

## Color

- **Layers:** neutrals 70–90% of pixels (`--bg/--surface/--fg/--muted/--border`) · one accent 5–10% · semantic 0–5% · effect <1% (gradients, glows — rarely justified).
- **Accent discipline:** ≤ 2 visible uses per screen (one eyebrow + one CTA, or one accent card + one tab). Links count as accent — demote to `--fg` underline when a CTA shares the screen. Hover/focus rings count; ration accordingly.
- **Contrast gates:** body text 4.5:1 · large text (≥24px, or ≥18.7px bold) 3:1 · UI components against adjacent surfaces 3:1. The linter computes and prints the core pairs (`fg/bg`, `fg/surface`, `muted/bg`, `muted/surface`, `accent/bg`, `accent/surface`, `accent-on/accent`) per theme — fix every `✗`; treat `(large/UI only)` pairs as fills and display-size text, or step one shade darker for small copy.
- **Dark themes:** never `#000` / `#fff` — `#0f0f0f` bg, `#f0f0f0` fg. Prefer semi-transparent white borders (`rgba(255,255,255,0.08)`) over solid dark borders.
- **Naming by purpose** (`--accent`, `--success`), never by hue (`--blue-500`) — hue names lock out theming.

## State coverage (anything with stateful UI)

Every interactive element defines: default → hover → focus-visible → active → disabled. Data surfaces define: loading (skeleton or spinner), empty (an empty state that explains), error (recoverable, with a path forward). Forms define: helper text, validation timing (on blur/submit, not per keystroke), error message next to the field, success feedback. Never ship only the happy path. Playbooks for all five data states live in `references/ux-flows.md`; the component-by-component contracts live in `references/ui-patterns.md`.

## Accessibility baseline (WCAG 2.2 AA — measured, not vibes)

The linter enforces the static half: `lang`, `alt`, control labels, zoom, focus-visible, heading structure, computed contrast. The rest is a checklist:

- [ ] Keyboard: every action reachable with Tab/Enter/Esc alone; focus order matches reading order; focus visible at every stop.
- [ ] Zoom: usable at 200% with no horizontal scroll; `user-scalable=no` never ships (lint P1).
- [ ] Contrast: no `✗` pairs in the linter's contrast line; small accent text uses a darker shade, not the fill color.
- [ ] Labels: every control has a visible label or `aria-label`; field errors are linked to their field (lint P0).
- [ ] Targets ≥ 44px touch; spacing prevents mis-taps.
- [ ] Motion: `prefers-reduced-motion` path present wherever anything animates (`references/motion.md`).
- [ ] Color is never the only signal (status pills carry text, not just hue).
- [ ] Structure: one `h1`, headings in order, semantic landmarks — the lint checks the mechanical parts.

## Motion discipline

Durations, the three easing curves, choreography rules and the reduced-motion kill switch live in `references/motion.md`. Short version: motion explains a state change or it gets deleted; `transform`/`opacity` only; exits faster than enters; one memorable micro-interaction per artifact.

## Laws of UX (composition decisions)

- **Hick / choice overload:** pricing pages cap at 3–4 tiers; navigation caps at 5–7 links.
- **Von Restorff:** exactly one element per screen is allowed to be visually loud.
- **Pareto / selective attention:** dashboards put the 20% of metrics that matter above the fold.
- **Working memory:** never make the user hold a value across screens; show it.
- **Fitts:** primary actions are large and near the user's expected flow; destructive actions are small and confirmable.
- **Goal gradient / Zeigarnik:** progress indicators for multi-step flows; visible completion states.
- **Peak-end:** the final slide of a deck and the last section of a landing carry the strongest moment.

## Delivery checklist

**P0 — must pass**

- [ ] `python3 scripts/lint.py index.html` reports **zero P0** findings.
- [ ] No raw hex outside `:root` (grep `#[0-9a-fA-F]{3,8}` outside the token block).
- [ ] Accent ≤ 2 visible uses per screen; headings use `var(--font-display)`.
- [ ] All copy is brief-derived; zero filler, zero invented metrics.
- [ ] `data-design-id` on every top-level `<section>` (decks: `data-screen-label` on every slide).
- [ ] No `scrollIntoView()`; mobile reflow works at ≤ 920px.
- [ ] Decks only: every slide has a theme class; no 3+ same-theme in a row; the nav script is intact.
- [ ] A11y statics clear: `lang` present, every `<img>` has `alt`, every control has a label (all lint P0s).

**P1 — should pass**

- [ ] One decisive flourish per artifact. Section rhythm alternates (no two stat rows / quote blocks / feature triplets in a row).
- [ ] Headlines ≤ 14 words (deck covers ≤ 8). CTAs say what happens.
- [ ] Numerics in mono with tabular figures.
- [ ] One image style per page; content images keep intrinsic ratio and full frame.
- [ ] ALL-CAPS carries ≥ 0.06em tracking; display sizes carry negative tracking (Latin only).
- [ ] Decks: cover ≤ 8 words, one quote per deck, closing slide decisive; no overflow at 1280×800 and 1440×900.
- [ ] Linter contrast line: no `✗`; `(large/UI only)` pairs appear only at display/bold sizes or in fills.
- [ ] Any artifact that animates ships its reduced-motion path.
- [ ] Data surfaces cover loading / empty / error states (`ux-flows.md`), not only the happy default.

**P2 — nice to have**

- [ ] `text-wrap: pretty` on paragraphs, `balance` on headings.
- [ ] Derived tones via `color-mix()` instead of extra numbered tokens.
- [ ] Deck position persists across refresh; progress bar and counter always visible.
- [ ] Sticky chrome (nav / sidebar) uses a restrained frosted treatment if any.
- [ ] DESIGN.md dials visibly respected (density steps, motion budget).

## Reviewing an existing artifact

When asked to audit rather than build:

1. Run the linter — human output for reading, `--json` for pasting into a report.
2. Walk this file top to bottom against the artifact; note the section-level rhythm, not just mechanics.
3. Report findings as a table — **severity · id · where · fix** — P0 first, before touching anything.
4. Fix with surgical edits (never regenerate), re-run the lint, and show the before/after contrast line when it changed.

A review without the linter output is an opinion; with it, it's a checklist.

## The soul test

Screenshot the artifact. If someone outside the project can tell which product it belongs to, it has soul. If not, you shipped a template: add one detail only a user of the product would recognize (a real shortcut hint, a status badge with product-specific phrasing), one micro-interaction, or one bolder type decision.

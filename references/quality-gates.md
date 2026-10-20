# Quality gates — craft rules and the review checklist

Universal rules that apply on top of any DESIGN.md. The design system decides *which* values; this file decides *how* they behave. P0 = must pass before delivery; P1 = should pass; P2 = nice to have. `scripts/lint.py` auto-checks the mechanical half — run it early and often.

## The seven cardinal sins (P0, auto-checked by `scripts/lint.py`)

1. **Default LLM indigo as accent** — hardcoded `#6366f1`, `#4f46e5`, `#4338ca`, `#3730a3`, `#8b5cf6`, `#7c3aed`, `#a855f7` (anywhere outside a token block that legitimately defines `--accent`). Use `var(--accent)`.
2. **Two-stop "trust" gradient on a hero** — purple→blue, blue→cyan, indigo→pink. A flat obsidian or paper surface + architectural grid + intentional type beats it every time.
3. **Emoji as feature/UI icons** — `✨🚀🎯⚡🔥💡📈🎨🛡️🌟💪🎉👋🙌✅⭐🏆` inside headings, buttons, list items, icon classes. Use 1.5–1.8px-stroke monoline SVG or full schematic diagrams with `currentColor` / `var(--accent)`.
4. **Hardcoded font-family bypassing `--font-display`** — `h1`/`h2` must use `var(--font-display)`, never a raw hardcoded font name in a heading rule that ignores the token block.
5. **Rounded card with a colored left-border accent** — the canonical "AI dashboard tile". Drop either the radius or the left border.
6. **Invented metrics** — "10× faster", "99.9% uptime", "3× more productive". Use real brief-sourced metrics, architectural parameters (e.g., `sub-90ms cold start` when part of the brief), or labeled placeholders (`—`).
7. **Filler copy** — lorem ipsum, "Feature One / Two / Three", "placeholder text". An empty section is a composition problem, not a copy problem.

## Soft tells & low-craft traps (P1)

- **Plain-text feature triplets without visual schematics** — 3 small icons over a heading and paragraph with no `.bento-visual`, `.app-window`, `.term`, or SVG diagram reads like an unstyled 2018 boilerplate.
- **Hero with zero product proof** — a product landing page whose hero is only text + buttons floating in empty whitespace, lacking a `.hero-stage` (`.app-window`, `.term`, or architectural schematic).
-External placeholder image CDNs (unsplash, placehold.co, picsum, placekitten).
- More than ~12 raw hex values outside `:root`.
- `var(--accent)` used 6+ times inline in the rendered body.

## Slop vs. 2025–2026 Flagship Craft

Know the difference between generic LLM defaults and high-end 2025–2026 product design:

| Dimension | Generic AI Slop (Ban) | 2025–2026 Flagship Product Craft (Ship) |
|---|---|---|
| **Surface & Grid** | Floating rounded cards with drop shadows and `gap: 32px` on a purple-tinted background | **Exposed `1px` Hairline Bento (`.bento-hairline`)** with `gap: 1px; background: var(--border)`, flush cells, and subtle top-edge `--specular` highlight |
| **Hero Section** | Centered text + two pill buttons floating in empty space | **Hero + Product Stage (`.hero-stage`)**: Dual-tone or block-highlighted `h1` anchored by a multi-pane `.app-window` (IDE tree + agent trace + dot-matrix canvas) |
| **Feature Section** | 3 tiny `36×36px` SVG icons above generic blurbs | **Schematic Bento Cells (`.bento-visual`)** (latency arc gauges, isometric wireframe cubes, `FORK → BUILD → EVAL` DAG trees, wireframe globes) + **Numbered `01`–`04` Index Showcases (`.index-showcase`)** |
| **Headlines** | Uniform weight/color single-tone text | **Dual-Tone Hierarchy** (`<span class="tone-muted">Fast, Scalable</span> Infrastructure`) or **Solid Block Highlight** (`<mark class="tone-block">in minutes</mark>`) |
| **Button Contrast** | White text on bright green/cyan buttons (unreadable) | Tokenized `--accent-on` (`oklch(15% ...)` dark ink on luminous mint/green; crisp white on electric Klein blue) |

## Typography

- **Scale:** multiplicative (1.2 / 1.25), 6–8 sizes max per artifact. Display 44–72 · H1 32–48 · H2 24–32 · H3 18–22 · body 15–16 · small 13–14 · caption 11–12.
- **Leading:** display/H1 ≥32px → 1.04–1.12 (tight); body → 1.5–1.6; small → 1.45.
- **CJK overrides (not optional):** CJK glyphs fill the em box — display leading 1.3–1.4, body 1.7–1.8. Negative tracking is Latin-only; CJK display gets `0`.
- **Letter-spacing:** body `0` · small text `+0.01–0.02em` · **ALL CAPS `+0.06–0.1em` (required)** · headings 32px+ `-0.02em` · display 48px+ `-0.025em to -0.03em`.
- **Pairs:** max 2–3 typefaces per artifact (`--font-display`, `--font-body`, `--font-mono`), always with system fallbacks. Use `var(--font-mono)` for structural chrome: numbered index tabs (`01`–`04`), `.mono-title` bento headings, CLI pills, and tabular numbers.
- **Line length:** 50–70 characters (`max-width: 60ch`).

## Color & Surface Physics

- **Layers:** neutrals 85–92% of pixels (`--bg`, `--surface`, `--surface-2`, `--fg`, `--muted`, `--border`) · one signal accent 5–10% (`--accent` + `--accent-on`) · semantic 0–5%.
- **Accent discipline:** ≤ 2 visible uses per screen (e.g., eyebrow/active-tab + primary CTA, plus subtle schematic stroke).
- **Contrast gates:** body text 4.5:1 · large text (≥24px, or ≥18.7px bold) 3:1 · UI components against adjacent surfaces 3:1 · `accent-on/accent` ≥ 4.5:1. The linter computes and prints all core pairs per theme — fix every `✗`.
- **Dark-native flagship themes:** Use deep obsidian/carbon (`oklch(12%–14% ...)`) for `--bg`, stepped charcoal (`oklch(16%–21% ...)`) for `--surface` and `--surface-2`, and crisp `1px` structural borders (`oklch(24%–26% ...)`).

## State coverage (anything with stateful UI)

Every interactive element defines: default → hover → focus-visible → active → disabled. Data surfaces define: loading, empty, error. Playbooks for all five data states live in `references/ux-flows.md`; component contracts live in `references/ui-patterns.md`.

## Accessibility baseline (WCAG 2.2 AA — measured, not vibes)

- [ ] Keyboard: every action reachable with Tab/Enter/Esc alone; `:focus-visible` ring on every stop.
- [ ] Zoom: usable at 200% with no horizontal scroll; `user-scalable=no` never ships (lint P1).
- [ ] Contrast: no `✗` pairs in the linter's contrast line, including `accent-on/accent`.
- [ ] Labels: every control has a visible label or `aria-label` (lint P0).
- [ ] Motion: `prefers-reduced-motion` path present wherever anything animates (`references/motion.md`).
- [ ] Structure: one `h1`, headings in order, semantic landmarks.
- [ ] **Rendered:** `python3 scripts/verify.py index.html` reports zero P0 — computed contrast, no sideways scroll, no clipped text, no runtime error.

## The two gates

| Gate | Reads | Catches | Needs |
|---|---|---|---|
| `scripts/lint.py` | the source | slop, raw hex, token names, structure, static a11y | nothing |
| `scripts/verify.py` | the rendered page | horizontal overflow, clipped text, computed contrast, tap targets, runtime errors | Chrome/Chromium |

Run both. The linter is fast and deterministic; the verifier is the one that sees what a human sees. A file can pass the linter and still scroll sideways at 390px — that is exactly what the verifier is for.

## Delivery checklist

**P0 — must pass**

- [ ] `python3 scripts/lint.py index.html` reports **zero P0** findings.
- [ ] `python3 scripts/verify.py index.html` reports **zero P0** findings (skip only when no Chrome is installed — say so).
- [ ] No raw hex outside `:root` (grep `#[0-9a-fA-F]{3,8}` outside the token block).
- [ ] `--accent-on` defined in `:root`; `accent-on/accent` passes contrast check.
- [ ] Accent ≤ 2 visible uses per screen; headings use `var(--font-display)`.
- [ ] All copy is brief-derived; zero filler, zero invented metrics.
- [ ] `data-design-id` on every top-level `<section>` (decks: `data-screen-label` on every slide).
- [ ] No `scrollIntoView()`; mobile reflow works at ≤ 920px.
- [ ] A11y statics clear: `lang` present, every `<img>` has `alt`, every control has a label.
- [ ] Copy passes the two automated rules: no generic error phrase, no vague button label (`references/copy.md`).

**P1 — should pass (Flagship Craft Bar)**

- [ ] **Hero Product Stage present:** Landing page hero includes an `.app-window` multi-pane studio/runtime preview, live `.term` console, or detailed SVG schematic.
- [ ] **Schematic Bento / Indexed Features:** Feature sections use `.bento-hairline` with `.bento-visual` diagrams (gauges, isometric layers, DAG node trees, wireframe globes) or `.index-showcase` (`01`–`04` tabs) — never 3 bare icons over text.
- [ ] **Dual-tone or block-highlight headlines:** `h1`/`h2` uses `.tone-muted` or `.tone-block` for deliberate typographic hierarchy.
- [ ] Headlines ≤ 14 words (deck covers ≤ 8). CTAs say what happens.
- [ ] Numerics in mono with `font-variant-numeric: tabular-nums`.
- [ ] ALL-CAPS carries ≥ 0.06em tracking; display sizes carry negative tracking (Latin only).
- [ ] Linter contrast line: no `✗`.

## The soul test

Screenshot the artifact. Does it look like a flagship 2025–2026 release from a top design engineering team (exposed `1px` hairline architecture, multi-pane product stage, bespoke SVG telemetry schematics, razor-sharp typography)? If it looks like a plain text document with three icons, upgrade the hero stage and bento schematics before delivering.

# Deck contract — horizontal-swipe HTML presentations

A deck is a single HTML file where each `<section class="slide">` is one slide, the page scrolls horizontally with `scroll-snap`, and one small script drives navigation and the counter.

## Slide anatomy

```html
<section class="slide hero light center" data-screen-label="01 Cover">
  <div class="eyebrow">Context · Date</div>
  <h1 class="h-hero">One sharp sentence.</h1>
  <p class="lead">One concrete subhead.</p>
</section>
```

- **Theme class on every slide**, exactly one of: `light` · `dark` · `hero light` · `hero dark`. A bare `class="slide"` is a regression.
- `center` for cover, big-stat, big-quote slides; left-aligned for content slides.
- `data-screen-label="01 Cover"` on every slide (chat can then say "edit slide 5").
- The `.slide.active` / `.slide.is-active` class must track the visible slide — host preview bridges read it for the slide counter.

## Theme rhythm (the rule that prevents sleepiness)

Sketch the sequence **before writing HTML**, e.g. for 8 slides:

```
01 hero light center  Cover
02 light              Problem
03 hero dark center   Big stat
04 light              Three points
05 dark               Pipeline
06 hero light center  Quote
07 light              Before / after
08 hero dark center   Ask
```

- No 3+ same-theme slides in a row.
- For 8+ slides: ≥ 1 `hero dark` AND ≥ 1 `hero light`.
- Alternate light/dark roughly every 3–4 slides as breathing room.

Slide count by talk length: 5–10 min ≈ 6 · 15 min ≈ 8–10 · 20–30 min ≈ 12–18.

## Layout library (default set)

| # | Layout | Theme | Notes |
|---|---|---|---|
| 1 | Cover | `hero light center` | eyebrow + `.h-hero` ≤ 8 words + one lead line |
| 2 | Body / statement | `light` or `dark` | eyebrow + `.h-xl` headline + ≤ 2 sentences |
| 3 | Three points | `light` | 3 columns, hairline top rules, one idea each |
| 4 | Big stat | `hero dark center` | ONE number (mono/display), one caption line |
| 5 | Pipeline / steps | `dark` or `light` | 3–4 numbered steps, mono numerals |
| 6 | Quote | `hero light center` | one quote per deck, attribution line |
| 7 | Before / after | `light` | two columns, labels in mono uppercase |
| 8 | Ask / closing | `hero dark center` | decisive takeaway or ask, optional date |

## Copy rules

- Cover headline ≤ 8 words; body headlines ≤ 14.
- One number per big-stat slide — three numbers get three slides.
- One quote per deck.
- Closing slide is decisive (ask, takeaway, date) — not "Thank you".
- Numbers come from the brief or a real source; no invented metrics, no filler.

## Navigation runtime (keep intact)

The seed's script solves five iframe-specific problems — do not rewrite it:

1. Detect the real scroller (`document.scrollingElement` / `documentElement` / `body` — whichever actually overflows).
2. Listen for `scroll` on window **and** document, capture phase.
3. Listen for `keydown` on window **and** document, capture phase.
4. Auto-focus body on load and pointer interaction so keys work without a click.
5. Never use `scrollIntoView()` — it can yank the host page.

Required behavior:

- **Keyboard:** `→` / `↓` / `PageDown` / `Space` next; `←` / `↑` / `PageUp` / `Home` / `End` navigate; ignore events from inputs, textareas, editable regions.
- **Wheel / trackpad:** accumulate `deltaX + deltaY`; past a small threshold advance exactly one slide; reset quickly so one gesture never overshoots.
- **Touch:** horizontal swipe ≥ ~50px, greater than vertical movement, moves prev/next.
- **Dots:** one clickable button per slide; active dot marked `aria-current="true"`; updated on every navigation path.
- **Chrome:** visible counter (`n / N`), top progress bar, local position persistence (`localStorage`, restore on load).
- **Print:** a `@media print` block exposes every slide as a page — hide chrome, avoid clipped content.
- **Fallbacks:** without script, all slides render stacked and readable.

## Optional host interop

If the deck will be embedded in a host app that tracks slide position, add `data-deck-protocol="1"` on `<html>` and post `{type:'deck:slide-state', active, count}` to the parent on slide change. Standalone decks skip this.

## Export & handoff

- Single HTML file is the source of truth; print-to-PDF gives a shareable PDF; screenshots per slide for review.
- Speaker notes: keep them as HTML comments inside each slide, or a `<details>` block after the slide content.

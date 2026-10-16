# Motion — choreography for interfaces that move

Motion is a budget, not a decoration. Every animation must explain a state change (a thing appeared, moved, or responded) or it gets deleted. One memorable micro-interaction per artifact; three is a fidget.

## Durations (pick the smallest that reads)

| Job | Duration | Feeling |
|---|---|---|
| Hover / press feedback | 100–150ms | immediate, tactile |
| State change (toggle, tab, expand) | 150–250ms | connected to the input |
| Overlay enter/exit (modal, toast, sheet) | 250–400ms | spatial, deliberate |
| Page / slide transition | 300–500ms | cinematic — decks only |

Beyond 500ms is for moments the user explicitly asked for; never for chrome.

## Easing (memorize three curves)

```css
:root {
  --ease-standard: cubic-bezier(0.2, 0, 0, 1);      /* state changes, transforms */
  --ease-enter:    cubic-bezier(0.05, 0.7, 0.1, 1); /* things appearing: fast out */
  --ease-exit:     cubic-bezier(0.3, 0, 0.8, 0.15); /* things leaving: fast in */
}
```

- State change → `--ease-standard`.
- Enter (modal, toast, menu) → `--ease-enter`, from a plausible origin — a menu scales from its trigger, not the page center.
- Exit → `--ease-exit`, faster than the enter (~70% of the duration); the user has already moved on.
- Never `ease-in-out` on transforms; `linear` only for progress bars and marquees.
- No bounce, no elastic overshoot unless the brief is explicitly playful.

## What may move

- `transform` (translate/scale) and `opacity` only — they run on the compositor.
- Never animate `width`, `height`, `top`, `left`, `margin` (layout thrash).
- `transition: all` is a bug — name the properties.
- Color transitions are fine for hover: 150ms, `--ease-standard`.

## Choreography

- **One entrance per view.** A page-load sequence is a single orchestrated moment (heading → lead → CTA, 40–60ms stagger, max 5 items). Never re-trigger on scroll.
- **Hover is instant; tooltips wait.** Hover feedback starts within a frame; disclosure (tooltip, menu) waits ~150ms so pass-over doesn't flash.
- **Direction matches meaning.** Panels slide from the edge they return to; back-navigation reverses the forward animation.
- **Interruptible.** If an exit starts mid-enter, snap to the exit — never queue animations.
- **Reduced motion is a first-class path** (below), not an afterthought.

## Paste-ready recipes

Button press:

```css
.btn { transition: transform 120ms var(--ease-standard), background 150ms var(--ease-standard); }
.btn:active { transform: translateY(1px); }
```

Link underline slide:

```css
.link {
  background-image: linear-gradient(currentColor, currentColor);
  background-size: 0% 1px; background-position: 0 100%; background-repeat: no-repeat;
  transition: background-size 160ms var(--ease-standard);
}
.link:hover { background-size: 100% 1px; }
```

Toast in / out:

```css
.toast { transition: transform 250ms var(--ease-enter), opacity 200ms var(--ease-enter); }
.toast[data-state="closed"] { opacity: 0; transform: translateY(8px); transition-timing-function: var(--ease-exit); }
```

Skeleton shimmer (motion-consent only):

```css
@media (prefers-reduced-motion: no-preference) {
  .skeleton {
    background: linear-gradient(90deg, var(--fg-soft), transparent 40%, var(--fg-soft));
    background-size: 200% 100%;
    animation: skeleton 1.4s linear infinite;
  }
  @keyframes skeleton { to { background-position: -200% 0; } }
}
```

## Reduced motion (required, every artifact that animates)

Global kill switch:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

For meaningful movement (a progress reveal, a sheet), don't just speed it up — swap the transform for an opacity crossfade. Position/location cues get a non-spatial replacement.

## Motion QA

- [ ] Does every animation map to a state change? Delete the rest.
- [ ] Durations from the table; exits faster than enters.
- [ ] `transition: all` nowhere; no layout properties animated.
- [ ] Reduced-motion path present and honest (content still reachable).
- [ ] With motion off, nothing looks broken or half-arrived.

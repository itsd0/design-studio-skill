# Direction library — 5 curated visual directions

Used when there is no brand to match. Pick the best fit for the brief's tone and bind the palette and font stacks into the seed's `:root` **verbatim**. Each direction is deliberately distinct — do not blend two.

Palettes are OKLch values (modern browsers support `oklch()` and the seeds use `color-mix(in oklch, ...)` already). If the target must run in an ancient embedded browser, convert the values once with any OKLch→sRGB converter and keep the converted set in `:root`.

---

## 1 · Editorial — Monocle / FT magazine  `(id: editorial-monocle)`

**Use for:** explicitly editorial or publishing briefs. **Not** for commerce, SaaS, dashboards, utilities.
**Mood:** Print-magazine feel. Generous whitespace, large serif headlines, restrained palette of neutral paper + ink + one brand-justified accent.
**References:** Monocle, FT Weekend, NYT Magazine.

```css
:root {
  --bg:      oklch(98% 0.004 95);   /* neutral paper, not beige wash */
  --surface: oklch(100% 0.002 95);
  --fg:      oklch(20% 0.018 70);   /* ink */
  --muted:   oklch(48% 0.012 70);
  --border:  oklch(90% 0.006 95);
  --accent:  oklch(52% 0.10 28);    /* restrained editorial red */

  --font-display: 'Iowan Old Style', 'Charter', Georgia, serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  --font-mono:    ui-monospace, 'JetBrains Mono', Menlo, monospace;
}
```

**Posture:** serif display, sans body, mono metadata only · no shadows, no rounded cards — borders + whitespace do the work · one decisive image, cropped only at the bottom · eyebrow in mono uppercase, accent used at most twice · never peach/pink/orange-beige page washes.

---

## 2 · Modern minimal — Linear / Vercel  `(id: modern-minimal)`

**Use for:** software-native products, SaaS, docs, developer tools.
**Mood:** Quiet, precise, product-led. System fonts, crisp neutral foundations, a small but visible palette so the interface feels shipped rather than greyscale.
**References:** Linear, Vercel, Notion 2024, Stripe docs.

```css
:root {
  --bg:      oklch(99% 0.002 240);
  --surface: oklch(100% 0 0);
  --fg:      oklch(18% 0.012 250);
  --muted:   oklch(54% 0.012 250);
  --border:  oklch(92% 0.005 250);
  --accent:  oklch(58% 0.18 255);   /* cobalt */

  --font-display: -apple-system, BlinkMacSystemFont, 'SF Pro Display', system-ui, sans-serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'SF Pro Text', system-ui, sans-serif;
  --font-mono:    ui-monospace, 'JetBrains Mono', Menlo, monospace;
}
```

**Posture:** tight tracking on display sizes (−0.02em) · hairline borders only, shadows only on dropdowns/modals · mono numerics with `font-variant-numeric: tabular-nums` · sticky frosted nav · content-led layouts with one product illustration, device mockup, or chart when it clarifies · controlled color: primary action + one secondary signal + status colors; never flood cards with gradients.

---

## 3 · Human / approachable — Airbnb / Duolingo  `(id: human-approachable)`

**Use for:** consumer tools, marketplaces, wellness, education, AI assistants, indie SaaS.
**Mood:** Friendly and tactile without the generic cozy canvas. Clean neutral background, product-led color, generous radii, clear hierarchy.
**References:** Airbnb, Duolingo product surfaces, Miro, Mercury.

```css
:root {
  --bg:      oklch(98% 0.004 240);
  --surface: oklch(100% 0 0);
  --fg:      oklch(20% 0.02 240);
  --muted:   oklch(50% 0.018 240);
  --border:  oklch(90% 0.006 240);
  --accent:  oklch(56% 0.12 170);   /* brand-safe teal */

  --font-display: 'Söhne', 'Avenir Next', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'SF Pro Text', system-ui, sans-serif;
  --font-mono:    ui-monospace, Menlo, monospace;
}
```

**Posture:** sans display with strong weight contrast · radii 12–18px on a crisp grid · primary action + secondary/domain accent + status colors; color separates panels and states · subtle elevation on interactive cards; tasteful gradients allowed for hero/device/product moments only, never as a full-page pastel wash · avoid generic pastel gradients; use real screenshots, data, or labeled placeholders.

---

## 4 · Tech / utility — Datadog / GitHub  `(id: tech-utility)`

**Use for:** engineering and operations surfaces, dashboards, consoles, docs for technical products.
**Mood:** Data-dense, monospace-friendly. Information per square inch, not vibes.
**References:** Datadog, GitHub, Cloudflare dashboard, Sentry.

```css
:root {
  --bg:      oklch(98% 0.005 250);
  --surface: oklch(100% 0 0);
  --fg:      oklch(22% 0.02 240);
  --muted:   oklch(50% 0.018 240);
  --border:  oklch(90% 0.008 240);
  --accent:  oklch(58% 0.16 145);   /* signal green */

  --font-display: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', system-ui, sans-serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', system-ui, sans-serif;
  --font-mono:    'JetBrains Mono', 'IBM Plex Mono', ui-monospace, Menlo, monospace;
}
```

**Posture:** one sans family for display + body is acceptable — utility trumps editorial · tabular numerics everywhere; mono for code, IDs, hashes · dense tables with hairline borders, no row striping · inline status pills with restrained tinted backgrounds · avoid hero images, oversized headlines, and marketing copy — show the product.

---

## 5 · Brutalist / experimental — Are.na / Yale  `(id: brutalist-experimental)`

**Use for:** art, indie, agency, manifesto pages.
**Mood:** Loud type. Visible grid. System sans plus one oversized serif. Deliberate ugliness as confidence.
**References:** Are.na, Yale Center for British Art, mschf, Read.cv.

```css
:root {
  --bg:      oklch(98% 0.004 240);   /* neutral printer paper */
  --surface: oklch(100% 0 0);
  --fg:      oklch(15% 0.02 100);
  --muted:   oklch(40% 0.02 100);
  --border:  oklch(15% 0.02 100);    /* borders are full-strength fg */
  --accent:  oklch(60% 0.22 25);     /* hot red */

  --font-display: 'Times New Roman', 'Iowan Old Style', Georgia, serif;
  --font-body:    ui-monospace, 'IBM Plex Mono', 'JetBrains Mono', Menlo, monospace;
  --font-mono:    ui-monospace, 'IBM Plex Mono', 'JetBrains Mono', Menlo, monospace;
}
```

**Posture:** display serif at extreme sizes (`clamp(80px, 12vw, 200px)`) · body = monospace, deliberately · borders full-strength fg (1.5–2px), not muted greys · asymmetric layouts (70/30) · almost no border-radius (0–2px), no shadows, no gradients · underlined links, no hover decoration.

---

## Binding rules

- Bind the chosen direction's palette and fonts **verbatim**. Never improvise values from the label.
- If the user supplies an accent override ("moss green instead of cobalt"), modify `--accent` only and derive hover/active from it.
- Honor the posture cues in layout decisions — they are what makes the direction read as a direction rather than a palette swap.
- State the chosen direction in one sentence before building: `Direction: modern-minimal (cobalt on near-white, tight type).`

# The critique — how to review an artifact that passes the gates

The gates in `scripts/lint.py`, `scripts/verify.py` and `scripts/score.py` catch
the mechanical failures. They cannot tell you whether the page is *good*. This
file is the part that needs judgement — and, like every other skill in this
market, judgement gets better with worked examples. Each judgement below has a
before and an after.

Review in this order. Each step assumes the previous one passed.

---

## 1 · The claim

**Ask:** what does this page assert, in one sentence? If you cannot say it out
loud after reading the headline and the subhead, there is no page yet.

```html
<!-- before -->
<h1>Welcome to our revolutionary platform</h1>
<p>Our cutting-edge solution empowers teams to unlock seamless productivity.</p>

<!-- after -->
<h1>Ship a design review in an afternoon.</h1>
<p>Design Studio turns a brief into a single HTML file your team can open,
   print and send — no build step, no dependencies.</p>
```

**Tells:** "revolutionary", "seamless", "cutting-edge", "unlock", "empower",
"next-generation", "AI-powered". A claim nobody would say out loud is a
placeholder for a claim you have not made yet.

---

## 2 · The hierarchy

**Ask:** does the eye land on the claim first, then the action, then the
evidence? Everything else is structure.

- One `h1`. Not two, not none.
- The display size must be a *jump* from the section size — at least 1.8×.
  A 44px h1 above a 32px h2 is not a hierarchy, it is a typo.
- Body copy at 15–16px. If the body is 13px and the label is 11px, the label
  is doing the job of the body.

```css
/* before — no hierarchy, everything is a size apart */
h1 { font-size: 30px; } h2 { font-size: 22px; } p { font-size: 15px; }

/* after — the display size is a jump */
h1 { font-size: clamp(44px, 6vw, 72px); line-height: 1.02; letter-spacing: -.028em; }
h2 { font-size: clamp(28px, 3vw, 38px); line-height: 1.1; letter-spacing: -.02em; }
p  { font-size: 16px; line-height: 1.55; }
```

---

## 3 · The accent

**Ask:** can you point at the accent in one breath? Two moments, maximum, per
screen. A third one turns a signal into decoration.

```html
<!-- before — the accent is everywhere, so it means nothing -->
<button class="btn btn-primary">Start</button>
<a class="link">Learn more</a>
<span class="eyebrow">Pricing</span>
<p class="meta">Updated today</p>
<mark class="tone-block">Everything</mark>

<!-- after — one signal, one action -->
<button class="btn btn-primary">Start</button>
<a class="link">Learn more</a>
```

**Rule:** links demote to `--fg` whenever a CTA shares the screen.

---

## 4 · The surface

**Ask:** does the layout read as structure, or as floating cards? A page made
of cards has no hierarchy — the cards are the hierarchy, and they are all the
same.

```css
/* before — everything floats */
.card { background: white; border-radius: 12px; padding: 28px;
        box-shadow: 0 4px 24px rgba(0,0,0,.08); }

/* after — the grid is the structure */
.bento-hairline { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1px; background: var(--border); border: 1px solid var(--border);
  border-radius: 12px; overflow: hidden; }
.bento-cell { background: var(--surface); padding: 20px; }
```

**Tells:** `box-shadow` on a card that sits next to other cards; a `gap` above
24px between grid cells; a section that is one big card.

---

## 5 · The evidence

**Ask:** does the page show the product working, or describe it? A hero with a
paragraph about a dashboard is a paragraph about a dashboard.

**Require** a real artifact: a multi-pane window, a live trace, a chart with
real axes, a spec table, a schematic. Inline SVG counts; a screenshot of a
screenshot does not.

**Tells:** stock-photo hero; a device mockup containing lorem ipsum; a
"trusted by" row of grey logos that mean nothing.

---

## 6 · The states

**Ask:** what does this look like when the data is empty, loading, or wrong?
State coverage is the difference between a mockup and a product.

Every stateful surface defines: **loading · empty · error**. Every interactive
element defines: **default · hover · focus-visible · active · disabled**.

```html
<!-- before -->
<div class="panel"><div class="table"></div></div>

<!-- after -->
<div class="panel">
  <div class="skel" aria-hidden="true"><div class="skel-line w90"></div></div>
  <p class="sr-only">Loading transfers…</p>
</div>
```

**Tells:** an empty container with no message; a button with no disabled state;
focus rings removed with `outline: none` and nothing put back.

---

## 7 · The rhythm

**Ask:** does the page have a beat? Sections should feel like sentences —
different lengths, different densities, a moment of quiet after a dense one.

- Section spacing comes from a scale, not from a value typed per section.
- Alternate dense and open. A page where every section is equally weighted
  reads as a table of contents.
- One grid-break per page — the moment that makes someone look twice.

---

## 8 · The distance

**Ask:** would you recognise this page as *this product's*? Or as "an AI
landing page"?

The scorecard measures this: headline font, body font, accent family and
background family. **2/4 is the floor.** 3/4 is good. 4/4 means somebody chose.

```html
<!-- before — the default -->
<body style="background:#faf7f2">
  <h1 style="font-family:system-ui">Ship faster</h1>
  <p style="color:#6366f1">The AI-powered platform for modern teams.</p>
</body>
```

**Tells:** a cream ground with a teal accent and a serif headline — the exact
combination every model reaches for. System sans on both display and body.
Purple or indigo at any saturation.

---

## 9 · The handoff

**Ask:** could someone else ship this? A single self-contained file, a token
block, a `DESIGN.md` that says why the tokens are what they are, and a
screenshot for the PR.

- No external fonts, scripts or images. If it needs the network, it is not an
  artifact — it is a deployment.
- The contract is in the repo, not in someone's head.

---

## The order matters

Claim → hierarchy → accent → surface → evidence → states → rhythm → distance →
handoff. Each step is easier to judge once the previous one is right, and the
first two decide whether the rest is worth reviewing.

When something fails, fix it surgically. Do not regenerate the page — you will
throw away the seven decisions that were right.

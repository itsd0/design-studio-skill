# The design DNA library

Six reference systems, offline, MIT-licensed, and written for agents. Each one
is a complete, self-consistent set of decisions — tokens, type, spacing, radius,
elevation, component recipes and anti-patterns — that you can bind verbatim.

They are not brand styles to imitate. They are **starting grammars**: pick one,
bind its tokens, and let the brief decide the content. A library entry that
survives contact with your product is worth more than a hundred swatches.

## How to use one

1. Read the entry.
2. Copy its `:root` block into the artifact — verbatim, not approximately.
3. Copy its component recipes for the patterns it lists.
4. Keep the anti-patterns. They are the reason the entry works.
5. If your brief does not fit the entry, generate a different direction with
   `python3 scripts/directions.py --brief "…"` rather than bending this one.

## The entries

| File | Use it for | Distance from the default look |
|---|---|---|
| `dark-structural-grid.md` | developer tools, AI infrastructure, agent runtimes, observability | high — exposed hairline grids, one signal colour |
| `light-editorial-serif.md` | editorial, research, newsletters, long-form products | high — serif display, warm paper, terracotta |
| `monochrome-operator.md` | terminals, CLIs, admin consoles, log viewers | very high — mono-dominant, amber on graphite |
| `warm-human-soft.md` | health, community, education, consumer onboarding | high — humanist type, soft surfaces, rounded |
| `clinical-data.md` | dashboards of measurements, lab, finance, medical | medium-high — cool near-white, teal signal, dense but calm |
| `cinematic-ember.md` | studios, agencies, premium launches, portfolios | high — near-black, one ember accent, huge type |

## The rule the library exists to serve

> A skill used by everyone becomes the new default.

Every entry here is a *different* grammar on purpose. If your artifact is
shipped with the same type and palette as everyone else's, the library failed —
not the agent. Run `python3 scripts/score.py index.html` and read the
"distance from the default" line: **2/4 is the floor**, 3/4 is good, 4/4 means
you chose deliberately.

## Adding an entry

An entry earns its place when it is (a) a complete system, (b) verifiable with
`python3 scripts/verify.py` and `python3 scripts/score.py`, and (c) a grammar
that is not already covered. Copy the shape of an existing file; keep the
anti-patterns section — that is the part agents skip and reviewers need.

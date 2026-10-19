# Gallery

Artifacts built with Design Studio, and the evidence that they hold up.

## What belongs here

An artifact plus the three files that make it reviewable:

```
gallery/<slug>/
├── index.html      the artifact — single file, self-contained
├── DESIGN.md       the brand contract it was built from
└── screenshot.png  the first screen at 1440×900
```

A submission that arrives without a `DESIGN.md` is not a submission — the
contract is the part that makes the artifact reproducible, and reproducibility
is the whole point of this skill.

## The review

Every entry is reviewed with the same four questions the independent skill
evaluations use, and the same seven basic checks:

**Rules** — does the contract give concrete decisions (tokens, type scale,
spacing) rather than adjectives?
**Seeing** — did it get rendered and checked, or shipped on faith?
**Away from the default** — would you recognise it as this product's page, or
as "an AI landing page"? `python3 scripts/score.py index.html` reports the
distance; **2/4 is the floor**.
**Fidelity** — does the artifact do what the brief asked, with nothing
invented?

The seven checks: copy complete · nothing invented · one `h1` · a button above
the fold · no sideways scroll on a phone · no runtime errors · self-contained.

## The gates every entry must pass

```bash
python3 scripts/lint.py index.html        # 0 P0 · 0 P1
python3 scripts/verify.py index.html      # 0 P0 · 0 P1
python3 scripts/contract.py index.html    # 0 P0
python3 scripts/score.py index.html       # every check passes
```

CI runs the same four commands over the gallery, so an entry that stops
passing stops being published.

## Submitting

Open a pull request with the three files above, and a one-line note: what the
brief was, and which direction it took. The maintainer runs the gates and
either merges or tells you which gate failed.

## Benchmarks

`benchmarks/` holds published comparisons — one brief, more than one
direction, rendered side by side with the method's own tools:

| Benchmark | What it shows |
|---|---|
| `brief-01.html` | one brief, three candidate directions, rendered and compared |

The point of a benchmark is not to win. It is to make the method's decisions
visible: a reviewer can see which directions were considered, what each one
costs, and why the shipped one won.

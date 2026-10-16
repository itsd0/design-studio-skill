# Design Studio

A skill for [OpenCode](https://opencode.ai) that turns a brief into **polished, single-file HTML design artifacts** — landing pages, web/app prototypes, dashboards, and slide decks — with no build step and zero runtime dependencies.

The method: capture the brief → fix the brand in a `DESIGN.md` contract → plan before pixels → build from a seed → pass the quality gates → deliver one self-contained `index.html` you can open, ship, print to PDF, or screenshot.

## What's inside

| Path | Purpose |
|---|---|
| `SKILL.md` | The workflow the agent follows + non-negotiables |
| `references/design-md.md` | Brand contract: section order, standard token names |
| `references/directions.md` | 5 curated visual directions (palettes, fonts) |
| `references/artifact-contract.md` | Output rules: layout, imagery, dashboards, mobile, exports |
| `references/deck-contract.md` | Deck mode: slide themes, rhythm, navigation runtime |
| `references/quality-gates.md` | Anti-slop + craft rules, P0/P1/P2 review checklist |
| `assets/design-md.template.md` | Starter brand contract |
| `assets/prototype-seed.html` | Page/app seed: tokens + class system |
| `assets/section-skeletons.html` | 8 paste-ready sections (hero, features, stats, quote, CTA…) |
| `assets/deck-seed.html` | Deck seed: themes, chrome, nav runtime, print CSS |
| `scripts/lint.py` | Anti-slop linter (fails on P0, advises on P1/P2) |

## Install

Clone into your OpenCode skills directory (the directory name becomes the skill id):

```bash
gh repo clone itsd0/design-studio-skill ~/.config/opencode/skills/design-studio
# or over SSH:
git clone git@github.com:itsd0/design-studio-skill.git ~/.config/opencode/skills/design-studio
```

Reload OpenCode. **Design Studio** activates on design-related requests, or ask for it by name.

## Usage

Just ask:

- "Design a landing page for a coffee-subscription startup."
- "Prototype a dashboard for a homelab."
- "Build a 10-slide pitch deck as a single HTML file."
- "Review this index.html against the quality gates and fix what fails."

The agent writes a real `index.html`, runs the linter, and iterates until it passes.

## The linter

```bash
python3 scripts/lint.py index.html
```

Exit code `1` means at least one must-fix (P0) finding. Works on any single-file HTML artifact.

## Requirements

- Python 3 — for the linter only
- The artifacts themselves are plain HTML/CSS/JS: no dependencies, no build step

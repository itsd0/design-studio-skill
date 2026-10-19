#!/usr/bin/env python3
"""
Design Studio — direction studio.

Two things a design skill usually gets wrong:

1. It makes the agent pick a direction from a fixed list *blind* — nobody
   ever sees the alternatives.
2. The list becomes the house style. Every page starts to look the same.

This tool fixes both. It derives candidate directions from the brief
(procedurally, so the result is not a fixed menu), renders them side by
side, and hands the user one image to choose from.

Usage:
    python3 scripts/directions.py --brief "AI infrastructure for agents"
    python3 scripts/directions.py --brief "..." --count 3 --json
    python3 scripts/directions.py --brief "..." --sheet sheet.png
    python3 scripts/directions.py --list
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import verify  # noqa: E402

# ── the vocabulary ────────────────────────────────────────────────────────

PALETTES: list[dict] = [
    {
        "id": "obsidian-signal",
        "type_pref": ["grotesk", "mono-terminal", "geometric"],
        "name": "Obsidian Signal",
        "mood": "Dark, engineered, one phosphor signal cutting through the dark",
        "bg": "oklch(13% 0.006 255)", "surface": "oklch(16% 0.008 255)",
        "surface2": "oklch(20% 0.010 255)", "fg": "oklch(96% 0.004 255)",
        "muted": "oklch(68% 0.012 255)", "border": "oklch(24% 0.010 255)",
        "accent": "oklch(80% 0.17 152)", "accent-on": "oklch(15% 0.02 152)",
        "domains": ["ai", "agent", "infra", "devtool", "devops", "terminal",
                    "observability", "latency", "runtime", "platform"],
        "tones": ["technical", "dark", "engineered", "precise", "serious"],
    },
    {
        "id": "paper-editorial",
        "type_pref": ["editorial-serif", "humanist", "grotesk"],
        "name": "Paper Editorial",
        "mood": "Warm paper, serif authority, generous margins, ink on cream",
        "bg": "oklch(98% 0.006 85)", "surface": "oklch(99% 0.004 85)",
        "surface2": "oklch(95% 0.010 85)", "fg": "oklch(22% 0.012 60)",
        "muted": "oklch(48% 0.014 60)", "border": "oklch(88% 0.012 80)",
        "accent": "oklch(52% 0.14 35)", "accent-on": "oklch(98% 0.006 85)",
        "domains": ["editorial", "writing", "magazine", "journal", "essay",
                    "newsletter", "research", "book", "reading"],
        "tones": ["editorial", "warm", "calm", "considered", "humanist"],
    },
    {
        "id": "blueprint-grid",
        "type_pref": ["grotesk", "mono-terminal", "geometric"],
        "name": "Blueprint Grid",
        "mood": "Deep navy, exposed measurement grid, cyan schematic lines",
        "bg": "oklch(18% 0.03 255)", "surface": "oklch(22% 0.035 255)",
        "surface2": "oklch(27% 0.040 255)", "fg": "oklch(94% 0.02 240)",
        "muted": "oklch(70% 0.04 240)", "border": "oklch(34% 0.05 250)",
        "accent": "oklch(78% 0.13 210)", "accent-on": "oklch(16% 0.04 250)",
        "domains": ["engineering", "infra", "architecture", "cad", "simulation",
                    "data", "logistics", "network", "security"],
        "tones": ["technical", "precise", "measured", "cool", "systematic"],
    },
    {
        "id": "solar-terminal",
        "type_pref": ["mono-terminal", "grotesk", "geometric"],
        "name": "Solar Terminal",
        "mood": "Warm amber on near-black, monospace-dominant, operator console",
        "bg": "oklch(12% 0.012 70)", "surface": "oklch(16% 0.014 70)",
        "surface2": "oklch(21% 0.016 70)", "fg": "oklch(94% 0.02 90)",
        "muted": "oklch(66% 0.02 80)", "border": "oklch(27% 0.02 75)",
        "accent": "oklch(82% 0.15 85)", "accent-on": "oklch(15% 0.02 70)",
        "domains": ["terminal", "cli", "console", "shell", "ops", "system",
                    "admin", "server", "developer"],
        "tones": ["technical", "dark", "retro", "operator", "raw"],
    },
    {
        "id": "vellum-human",
        "type_pref": ["humanist", "editorial-serif", "grotesk"],
        "name": "Vellum Human",
        "mood": "Soft off-white, muted terracotta, rounded and unhurried",
        "bg": "oklch(97% 0.008 90)", "surface": "oklch(99% 0.004 90)",
        "surface2": "oklch(94% 0.012 90)", "fg": "oklch(28% 0.02 50)",
        "muted": "oklch(52% 0.018 55)", "border": "oklch(89% 0.014 85)",
        "accent": "oklch(58% 0.13 40)", "accent-on": "oklch(98% 0.01 90)",
        "domains": ["health", "wellness", "community", "education", "learning",
                    "nonprofit", "lifestyle", "care", "people"],
        "tones": ["warm", "human", "approachable", "soft", "friendly"],
    },
    {
        "id": "nord-frost",
        "type_pref": ["grotesk", "geometric", "humanist"],
        "name": "Nord Frost",
        "mood": "Cool near-white, slate text, one glacial blue, quiet confidence",
        "bg": "oklch(98% 0.004 250)", "surface": "oklch(100% 0 0)",
        "surface2": "oklch(95% 0.008 250)", "fg": "oklch(24% 0.02 250)",
        "muted": "oklch(52% 0.02 250)", "border": "oklch(90% 0.008 250)",
        "accent": "oklch(58% 0.13 245)", "accent-on": "oklch(99% 0 0)",
        "domains": ["saas", "productivity", "finance", "fintech", "analytics",
                    "dashboard", "workspace", "planning", "collaboration"],
        "tones": ["calm", "precise", "professional", "cool", "quiet"],
    },
    {
        "id": "ember-graphite",
        "type_pref": ["geometric", "editorial-serif", "grotesk"],
        "name": "Ember Graphite",
        "mood": "Neutral graphite with a single ember accent — cinematic restraint",
        "bg": "oklch(15% 0.004 250)", "surface": "oklch(19% 0.005 250)",
        "surface2": "oklch(24% 0.006 250)", "fg": "oklch(95% 0.003 250)",
        "muted": "oklch(66% 0.008 250)", "border": "oklch(30% 0.007 250)",
        "accent": "oklch(66% 0.19 40)", "accent-on": "oklch(15% 0.01 40)",
        "domains": ["studio", "agency", "creative", "film", "music", "design",
                    "portfolio", "premium", "luxury", "brand"],
        "tones": ["bold", "cinematic", "minimal", "dark", "confident"],
    },
    {
        "id": "clinical-lumen",
        "type_pref": ["grotesk", "humanist", "geometric"],
        "name": "Clinical Lumen",
        "mood": "White room, teal-green signal, clinical clarity, no ornament",
        "bg": "oklch(99% 0.002 200)", "surface": "oklch(100% 0 0)",
        "surface2": "oklch(96% 0.006 200)", "fg": "oklch(26% 0.02 220)",
        "muted": "oklch(54% 0.02 220)", "border": "oklch(91% 0.008 210)",
        "accent": "oklch(62% 0.11 195)", "accent-on": "oklch(99% 0.002 200)",
        "domains": ["health", "medical", "clinical", "science", "research",
                    "bio", "diagnostics", "pharma", "lab"],
        "tones": ["clean", "clinical", "precise", "calm", "scientific"],
    },
]

TYPE_PAIRS: list[dict] = [
    {
        "id": "grotesk",
        "display": "-apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Display', system-ui, sans-serif",
        "body": "-apple-system, BlinkMacSystemFont, 'Inter', 'SF Pro Text', system-ui, sans-serif",
        "mono": "ui-monospace, 'SF Mono', Menlo, monospace",
        "voices": ["technical", "precise", "professional", "systematic", "clean",
                   "measured", "engineered", "professional", "serious"],
    },
    {
        "id": "editorial-serif",
        "display": "'Iowan Old Style', 'Charter', Georgia, 'Times New Roman', serif",
        "body": "-apple-system, BlinkMacSystemFont, 'Inter', system-ui, sans-serif",
        "mono": "ui-monospace, 'SF Mono', Menlo, monospace",
        "voices": ["editorial", "considered", "warm", "authoritative", "calm",
                   "humanist", "premium"],
    },
    {
        "id": "humanist",
        "display": "'Avenir Next', 'Optima', 'Gill Sans', 'Trebuchet MS', system-ui, sans-serif",
        "body": "'Avenir Next', 'Optima', 'Gill Sans', 'Trebuchet MS', system-ui, sans-serif",
        "mono": "ui-monospace, 'SF Mono', Menlo, monospace",
        "voices": ["human", "approachable", "friendly", "warm", "humanist",
                   "calm", "people"],
    },
    {
        "id": "mono-terminal",
        "display": "ui-monospace, 'SF Mono', 'JetBrains Mono', Menlo, monospace",
        "body": "-apple-system, BlinkMacSystemFont, 'Inter', system-ui, sans-serif",
        "mono": "ui-monospace, 'SF Mono', Menlo, monospace",
        "voices": ["operator", "raw", "terminal", "retro", "technical"],
    },
    {
        "id": "geometric",
        "display": "'Avenir Next', 'Century Gothic', Futura, system-ui, sans-serif",
        "body": "-apple-system, BlinkMacSystemFont, 'Inter', system-ui, sans-serif",
        "mono": "ui-monospace, 'SF Mono', Menlo, monospace",
        "voices": ["bold", "modern", "confident", "minimal", "premium"],
    },
]

DENSITIES = {
    "airy": {"section": "120px", "gap": "28px", "radius": "14px", "pad": "28px"},
    "regular": {"section": "80px", "gap": "20px", "radius": "10px", "pad": "20px"},
    "compact": {"section": "48px", "gap": "12px", "radius": "6px", "pad": "14px"},
}


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def score_direction(palette: dict, words: set[str]) -> int:
    score = 0
    for term in palette["domains"]:
        if term in words:
            score += 3
    for term in palette["tones"]:
        if term in words:
            score += 2
    return score


def score_type(pair: dict, words: set[str]) -> int:
    return sum(2 for term in pair["voices"] if term in words)


def infer_density(words: set[str]) -> str:
    if {"dense", "compact", "data", "console", "monitor", "log", "trading",
        "marketplace", "trading"} & words:
        return "compact"
    if {"spacious", "airy", "editorial", "premium", "luxury", "cinematic",
        "magazine", "landing"} & words:
        return "airy"
    return "regular"


def generate(brief: str, count: int = 3) -> list[dict]:
    """Candidate directions derived from the brief."""
    words = tokenize(brief)
    ranked = sorted(PALETTES, key=lambda p: -score_direction(p, words))
    type_ranked = sorted(TYPE_PAIRS, key=lambda t: -score_type(t, words))
    density = infer_density(words)

    picked: list[dict] = []
    used_type: set[str] = set()
    for palette in ranked:
        # Pair each palette with a type voice that suits it — the palette
        # names its preferred voices in order, and the voice must also match
        # something the brief said.
        pair = None
        for tid in palette.get("type_pref", []):
            candidate = next((t for t in TYPE_PAIRS if t["id"] == tid), None)
            if candidate and candidate["id"] not in used_type:
                pair = candidate
                break
        if pair is None:
            pair = next(
                (t for t in type_ranked
                 if t["id"] not in used_type
                 and any(v in palette["tones"] for v in t["voices"])),
                next((t for t in type_ranked if t["id"] not in used_type), type_ranked[0]),
            )
        used_type.add(pair["id"])
        picked.append({
            "id": palette["id"],
            "name": palette["name"],
            "mood": palette["mood"],
            "tokens": {
                "--bg": palette["bg"],
                "--surface": palette["surface"],
                "--surface-2": palette["surface2"],
                "--fg": palette["fg"],
                "--muted": palette["muted"],
                "--border": palette["border"],
                "--accent": palette["accent"],
                "--accent-on": palette["accent-on"],
            },
            "fonts": {
                "--font-display": pair["display"],
                "--font-body": pair["body"],
                "--font-mono": pair["mono"],
            },
            "density": density,
            "spacing": DENSITIES[density],
            "why": _why(palette, pair, words),
        })
        if len(picked) >= count:
            break
    return picked


def _why(palette: dict, pair: dict, words: set[str]) -> str:
    hits = [t for t in palette["domains"] + palette["tones"] if t in words]
    if hits:
        return (f"Matches the brief's {', '.join(hits[:3])} cues. "
                f"{palette['mood']}. {pair['id'].replace('-', ' ')} type.")
    return (f"{palette['mood']}. A deliberate step away from the default "
            f"look — {palette['id'].replace('-', ' ')}.")


# ── the comparison sheet ──────────────────────────────────────────────────

HERO = """
<div class="hero">
  <p class="eyebrow">{eyebrow}</p>
  <h1>{headline}</h1>
  <p class="lead">{lead}</p>
  <div class="cta">
    <button class="btn btn-primary">{cta}</button>
    <button class="btn btn-secondary">Read the docs</button>
  </div>
  <div class="panel">
    <div class="panel-bar"><span class="dots"><i></i><i></i><i></i></span>
      <span>workspace · session</span></div>
    <div class="panel-body">
      <div class="cell"><span class="k">SIGNAL</span><span class="v">99.98%</span></div>
      <div class="cell"><span class="k">THROUGHPUT</span><span class="v">38.4 GB/s</span></div>
      <div class="cell"><span class="k">REGIONS</span><span class="v">12</span></div>
    </div>
  </div>
</div>
"""

SHEET_CSS = """
* { box-sizing: border-box; }
body { margin: 0; background: #0c0c0d; font-family: -apple-system, system-ui, sans-serif; }
.sheet { display: grid; grid-template-columns: repeat(var(--cols, 3), 1fr); gap: 28px; padding: 28px; }
.variant { border-radius: 12px; overflow: hidden; border: 1px solid #26262a; }
.variant .tag { font: 11px/1 ui-monospace, monospace; letter-spacing: .08em;
  text-transform: uppercase; color: #8a8a92; padding: 10px 12px; background: #121214; }
.frame { background: var(--bg); color: var(--fg); padding: 34px 30px 30px; }
.hero h1 { font-family: var(--font-display); font-size: 34px; line-height: 1.04;
  letter-spacing: -.028em; margin: 0 0 14px; font-weight: 600; }
.hero .eyebrow { font-family: var(--font-mono); font-size: 11px; letter-spacing: .1em;
  text-transform: uppercase; color: var(--accent); margin: 0 0 16px; }
.hero .lead { font-family: var(--font-body); font-size: 14.5px; line-height: 1.55;
  color: var(--muted); margin: 0 0 22px; max-width: 42ch; }
.cta { display: flex; gap: 10px; margin-bottom: 26px; }
.btn { font-family: var(--font-body); font-size: 13px; font-weight: 500;
  padding: 10px 16px; border-radius: var(--radius); border: 1px solid transparent; }
.btn-primary { background: var(--accent); color: var(--accent-on); }
.btn-secondary { background: transparent; color: var(--fg); border-color: var(--border); }
.panel { border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
.panel-bar { display: flex; align-items: center; gap: 8px; padding: 9px 12px;
  background: var(--surface); border-bottom: 1px solid var(--border);
  font-family: var(--font-mono); font-size: 11px; color: var(--muted); }
.dots { display: inline-flex; gap: 4px; }
.dots i { width: 7px; height: 7px; border-radius: 50%; background: var(--border); }
.panel-body { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px;
  background: var(--border); }
.cell { background: var(--surface); padding: 12px 13px; display: flex;
  flex-direction: column; gap: 5px; }
.cell .k { font-family: var(--font-mono); font-size: 9.5px; letter-spacing: .08em;
  color: var(--muted); }
.cell .v { font-family: var(--font-mono); font-size: 17px; color: var(--fg); }
"""


def build_sheet(directions: list[dict], brief: str) -> str:
    cols = len(directions)
    variants = []
    for d in directions:
        style = ";".join(f"{k}:{v}" for k, v in
                         list(d["tokens"].items()) + list(d["fonts"].items())
                         + [("--radius", d["spacing"]["radius"])])
        variants.append(
            f'<div class="variant"><div class="tag">{d["name"]} · {d["density"]}</div>'
            f'<div class="frame" style="{style}">'
            + HERO.format(
                eyebrow=f"{d['id'].replace('-', ' ')} · {d['density']}",
                headline="One claim, stated plainly.",
                lead="A short paragraph that says what the product does, who it is for, "
                     "and what changes when it is in place.",
                cta="Start building",
            )
            + "</div></div>"
        )
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<style>:root{{--cols:{cols}}}{SHEET_CSS}</style></head>"
        f"<body><div class='sheet'>{''.join(variants)}</div></body></html>"
    )


def render_sheet(directions: list[dict], brief: str, out: Path) -> bool:
    chrome = verify.find_chrome()
    if not chrome:
        return False
    html = build_sheet(directions, brief)
    with tempfile.TemporaryDirectory(prefix="design-studio-sheet.") as tmp:
        tmpdir = Path(tmp)
        page = tmpdir / "sheet.html"
        page.write_text(html, encoding="utf-8")
        out.parent.mkdir(parents=True, exist_ok=True)
        # The card is a fixed height — render close to it so the sheet has no
        # dead space below the variants.
        stdout, stderr, code = verify.run_chrome(
            chrome, page.resolve().as_uri(), 1440, 620, tmpdir / "profile", 45,
            dump=False, screenshot=out,
        )
    return out.exists()


# ── CLI ───────────────────────────────────────────────────────────────────


def main(argv: list[str]) -> int:
    brief = ""
    count = 3
    as_json = False
    sheet = None
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--brief":
            i += 1
            brief = argv[i] if i < len(argv) else ""
        elif a == "--count":
            i += 1
            count = int(argv[i]) if i < len(argv) else 3
        elif a == "--sheet":
            i += 1
            sheet = Path(argv[i]) if i < len(argv) else Path("directions.png")
        elif a == "--json":
            as_json = True
        elif a == "--list":
            for p in PALETTES:
                print(f"{p['id']:<22} {p['name']:<20} {p['mood']}")
            return 0
        i += 1

    if not brief:
        print(__doc__.strip())
        return 2

    directions = generate(brief, count)

    if sheet:
        ok = render_sheet(directions, brief, sheet)
        if not ok:
            print("directions · could not render the sheet (no Chrome?)", file=sys.stderr)
            return 1
        if not as_json:
            print(f"directions · wrote {sheet}")
            for d in directions:
                print(f"  · {d['name']:<20} {d['id']}")
            print("  Pick one, then bind its tokens verbatim in :root.")
        else:
            print(json.dumps({"sheet": str(sheet), "directions": directions}, indent=2))
        return 0

    if as_json:
        print(json.dumps({"brief": brief, "directions": directions}, indent=2))
        return 0

    print(f"directions · {brief!r} → {len(directions)} candidates\n")
    for i, d in enumerate(directions, start=1):
        print(f"{i}. {d['name']}  ({d['id']}, density {d['density']})")
        print(f"   {d['why']}")
        print(f"   bg {d['tokens']['--bg']} · fg {d['tokens']['--fg']} · "
              f"accent {d['tokens']['--accent']}")
        print(f"   display {d['fonts']['--font-display'][:52]}…")
        print()
    print("Render them side by side and let the user choose:")
    print(f"   python3 scripts/directions.py --brief {brief!r} --sheet sheet.png")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

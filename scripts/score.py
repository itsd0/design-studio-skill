#!/usr/bin/env python3
"""
Design Studio — craft scorecard.

Renders an artifact and scores it against the checks a design review
actually makes: hierarchy, type discipline, accent budget, section
rhythm, content completeness, motion, and self-containment.

It also reports the metric that separates a design skill from a style
guide: how far the artifact sits from the default AI look (headline font,
body font, accent family, background family). Zero means "the same page
every agent produces".

Usage:
    python3 scripts/score.py index.html
    python3 scripts/score.py index.html --json
    python3 scripts/score.py index.html --shot card.png

Exit code 1 when a must-fix check fails.
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import verify  # noqa: E402

SCORE_PROBE = Path(__file__).resolve().parent / "probe-score.js"

MAX_ACCENT_USES = 12  # the visible budget is 2; this counts DOM occurrences


class Check:
    def __init__(self, cid: str, label: str, ok: bool | None, detail: str, fix: str = "",
                 weight: int = 1):
        self.id = cid
        self.label = label
        self.ok = ok          # True = pass, False = fail, None = not applicable
        self.detail = detail
        self.fix = fix
        self.weight = weight

    def as_dict(self) -> dict:
        return {"id": self.id, "label": self.label, "ok": self.ok,
                "detail": self.detail, "fix": self.fix, "weight": self.weight}


def collect(html: str, chrome: str, timeout: int = 45) -> dict | None:
    probe = SCORE_PROBE.read_text(encoding="utf-8")
    injected = verify.inject_probe(html, probe)
    with tempfile.TemporaryDirectory(prefix="design-studio-score.") as tmp:
        tmpdir = Path(tmp)
        page = tmpdir / "page.html"
        page.write_text(injected, encoding="utf-8")
        stdout, stderr, code = verify.run_chrome(
            chrome, page.resolve().as_uri(), 1440, 900, tmpdir / "profile", timeout, dump=True
        )
        if not stdout:
            return None
        return verify.extract_result(stdout, "__ds_score__")


def build_checks(data: dict, raw_html: str) -> list[Check]:
    checks: list[Check] = []
    h = data.get("hierarchy", {})
    t = data.get("type", {})
    a = data.get("accent", {})
    r = data.get("rhythm", {})
    c = data.get("content", {})
    m = data.get("motion", {})
    d = data.get("defaultDistance", {})
    kind = data.get("kind", "page")
    is_deck = kind == "deck"

    # ── hierarchy ──
    checks.append(Check(
        "one-h1", "Exactly one h1", h.get("h1Count") == 1,
        f"{h.get('h1Count', 0)} h1 element(s)",
        "A page has one h1 — it is the page's claim.",
    ))

    cta = h.get("firstCta")
    if cta:
        checks.append(Check(
            "cta-above-fold", "A call to action above the fold", True,
            f"first CTA: “{cta['text']}” at y={cta['top']}px",
            "",
        ))
    else:
        checks.append(Check(
            "cta-above-fold", "A call to action above the fold", None,
            f"no call to action — this is a {kind}, not a conversion page",
            "Put the primary action where the claim is.",
        ))

    order = h.get("headings", [])
    jumps = [order[i + 1] - order[i] for i in range(len(order) - 1) if order[i + 1] - order[i] > 1]
    checks.append(Check(
        "heading-order", "Headings descend without skipping", not jumps,
        "no skipped levels" if not jumps else f"{len(jumps)} skipped level(s)",
        "Never jump from h2 to h4 — the outline is the structure.",
    ))

    # ── type ──
    if t.get("displayToken"):
        checks.append(Check(
            "display-font-bound", "The h1 uses the display face", bool(t.get("displayBound")),
            f"h1 font: {h.get('h1Font', '?')}",
            "Bind the display stack to the headline — the type has a job.",
        ))
    else:
        checks.append(Check(
            "display-font-bound", "The h1 uses the display face", None,
            "no --font-display token — nothing to bind",
            "Bind the display stack to the headline — the type has a job.",
        ))

    sizes = t.get("distinctSizes", 0)
    checks.append(Check(
        "type-scale", "A tight type scale per screen", None if is_deck else sizes <= 10,
        f"{sizes} distinct sizes in the first two screens"
        + (" — slides keep their own scales" if is_deck else ""),
        "More than ten sizes on a screen reads as noise, not hierarchy.",
    ))

    fams = t.get("distinctFamilies", 0)
    checks.append(Check(
        "font-families", "At most three font families per screen", fams <= 3,
        f"{fams} families in the first two screens",
        "Display, body, mono. A fourth family is decoration.",
    ))

    # ── accent ──
    uses = a.get("uses", 0)
    first = a.get("usesInFirstScreen", uses)
    checks.append(Check(
        "accent-budget", "The accent stays rare on the first screen", first <= 4,
        f"{first} accent moment(s) above the fold, {uses} across the page",
        "At most two visible accent moments per screen — the rest is structure.",
    ))

    # ── rhythm ──
    ratio = r.get("anchoredRatio", 1)
    checks.append(Check(
        "section-anchors", "Every section is anchored", ratio >= 1.0,
        f"{r.get('sectionsAnchored', 0)}/{r.get('sections', 0)} sections carry data-design-id",
        "Anchor each section so a reviewer can point at it.",
    ))

    paddings = r.get("sectionPaddings", {})
    distinct = len(paddings)
    checks.append(Check(
        "section-rhythm", "Section spacing comes from a scale",
        None if not r.get("sections") else distinct <= 4,
        f"{distinct} distinct section paddings"
        + ("" if r.get("sections") else " — the page has no <section> elements"),
        "One spacing scale, used consistently — rhythm is repetition.",
    ))

    # ── content ──
    placeholders = c.get("placeholders", 0)
    checks.append(Check(
        "no-placeholders", "No unfilled placeholders", placeholders == 0,
        f"{placeholders} placeholder(s) left",
        "Replace every [REPLACE] — or state plainly what is still missing.",
    ))

    empty = c.get("emptySections", 0)
    checks.append(Check(
        "no-empty-sections", "No empty sections", empty == 0,
        f"{empty} section(s) with no copy",
        "Delete the section or write the copy — an empty section is a hole.",
    ))

    ext = c.get("externalResources", 0)
    checks.append(Check(
        "self-contained", "The artifact is self-contained", ext == 0,
        f"{ext} external resource(s)",
        "Inline everything — an artifact that needs the network is not an artifact.",
    ))

    words = c.get("words", 0)
    checks.append(Check(
        "copy-substance", "The copy says something", words >= 40,
        f"{words} words",
        "A landing page with no copy is a template, not a product.",
    ))

    # ── motion ──
    animated = m.get("animatedElements", 0)
    if animated == 0:
        checks.append(Check(
            "reduced-motion", "A reduced-motion path ships", None,
            "nothing animates — no reduced-motion path needed",
            "Ship the reduced-motion path whenever anything animates.",
        ))
    else:
        checks.append(Check(
            "reduced-motion", "A reduced-motion path ships", m.get("reducedMotionPath", False),
            "prefers-reduced-motion block found" if m.get("reducedMotionPath")
            else f"{animated} animated element(s), no reduced-motion block",
            "Ship the reduced-motion path whenever anything animates.",
        ))

    # ── source hygiene: raw colour in the CSS outside the token block ──
    without_comments = re.sub(r"<!--[\s\S]*?-->", "", raw_html)
    css = "\n".join(re.findall(r"<style[^>]*>([\s\S]*?)</style>", without_comments, re.I))
    css_without_root = re.sub(r":root\s*\{[^}]*\}", "", css)
    raw_hex = re.findall(r"#[0-9a-fA-F]{3,8}\b", css_without_root)
    checks.append(Check(
        "tokens-only", "No raw colour in the CSS outside the token block", not raw_hex,
        f"{len(raw_hex)} raw hex value(s) outside :root"
        + (f" ({', '.join(raw_hex[:4])})" if raw_hex else ""),
        "Every colour comes from a token — that is what makes them changeable.",
    ))

    # ── distance from the default ──
    distance = d.get("score", 0)
    checks.append(Check(
        "away-from-default", "The page is not the default look", distance >= 2,
        f"{distance}/4 away from the default "
        f"({', '.join(d.get('away', [])) or 'matches the house style'})",
        "Change the headline face, the accent family or the background family — "
        "a skill used by everyone becomes the new default.",
        weight=2,
    ))

    return checks


def main(argv: list[str]) -> int:
    as_json = "--json" in argv
    shot = None
    files: list[str] = []
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--shot":
            i += 1
            shot = Path(argv[i]) if i < len(argv) else Path("score.png")
        elif not a.startswith("-"):
            files.append(a)
        i += 1

    if not files:
        print(__doc__.strip())
        return 2

    chrome = verify.find_chrome()
    if not chrome:
        print("score · no Chrome or Chromium found — cannot render the artifact.",
              file=sys.stderr)
        return 2

    exit_code = 0
    for name in files:
        path = Path(name)
        if not path.is_file():
            print(f"score · {name}\n  skipped — file not found\n")
            continue
        raw = path.read_text(encoding="utf-8")
        data = collect(raw, chrome)
        if not data:
            print(f"score · {name}\n  ERROR — the artifact could not be rendered\n")
            exit_code = 1
            continue

        checks = build_checks(data, raw)
        passed = sum(1 for c in checks if c.ok is True)
        failed = sum(1 for c in checks if c.ok is False)
        na = sum(1 for c in checks if c.ok is None)
        total = len(checks)
        distance = data.get("defaultDistance", {}).get("score", 0)

        if as_json:
            print(json.dumps({
                "path": name,
                "kind": data.get("kind", "page"),
                "passed": passed,
                "failed": failed,
                "notApplicable": na,
                "total": total,
                "defaultDistance": distance,
                "away": data.get("defaultDistance", {}).get("away", []),
                "checks": [c.as_dict() for c in checks],
            }, indent=2))
        else:
            print(f"score · {name}  ({data.get('kind', 'page')})")
            for c in checks:
                if c.ok is None:
                    print(f"  n/a  {c.id:<22} {c.detail}")
                else:
                    mark = "ok  " if c.ok else "FAIL"
                    print(f"  {mark} {c.id:<22} {c.detail}")
                    if not c.ok and c.fix:
                        print(f"       fix: {c.fix}")
            print(f"  {passed}/{total} checks passed"
                  + (f" · {na} not applicable" if na else "")
                  + f" · {distance}/4 away from the default "
                  f"({', '.join(data.get('defaultDistance', {}).get('away', [])) or 'house style'})")
            print()

        if failed:
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv))

#!/usr/bin/env python3
"""
Design Studio lint self-tests.

Two suites:

1. Rule fixtures (tests/fixtures/*.html) — every rule must fire on a bad
   fixture and stay quiet on the good one.
2. Shipped artifacts (assets/*.html, demo/*.html) — the files we publish
   must lint with zero P0 findings.

Run:  python3 tests/run_tests.py   (from the skill root)
Exit: 1 if any case fails.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from lint import lint  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"

# (fixture, must_fire_ids, must_not_fire_ids)
CASES = [
    (
        "good.html",
        [],
        ["ai-default-indigo", "purple-gradient", "contrast-text", "img-alt",
         "input-unlabeled", "lang-missing", "focus-removed", "heading-structure"],
    ),
    (
        "bad-slop.html",
        ["purple-gradient", "emoji-icon", "left-accent-card", "filler-copy",
         "invented-metric", "all-caps-no-tracking"],
        ["ai-default-indigo"],  # suppressed once the gradient fires — by design
    ),
    (
        "bad-a11y.html",
        ["lang-missing", "img-alt", "input-unlabeled", "zoom-blocked",
         "justify-text", "focus-removed", "heading-structure", "heading-order"],
        [],
    ),
    ("bad-contrast.html", ["contrast-text"], []),
    ("bad-deck.html", ["slide-theme-missing", "slide-rhythm"], []),
    ("bad-dashboard.html", ["dashboard-missing-craft"], ["missing-visual-craft"]),
]


def run_fixtures() -> int:
    failures = 0
    print("· rule fixtures")
    for name, must, must_not in CASES:
        html = (FIXTURES / name).read_text(encoding="utf-8")
        findings = lint(html)
        ids = {f.id for f in findings}
        missing = [i for i in must if i not in ids]
        extra = [i for i in must_not if i in ids]
        if name == "good.html":
            p0 = [f.id for f in findings if f.severity == "P0"]
            if p0:
                missing.extend(f"no-P0 (found {', '.join(p0)})")
        ok = not missing and not extra
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
        if missing:
            print(f"       missing expected: {', '.join(missing)}")
        if extra:
            print(f"       unexpected: {', '.join(extra)}")
        failures += 0 if ok else 1
    return failures


def run_shipped() -> int:
    failures = 0
    print("· shipped artifacts (zero P0 required)")
    files = [ROOT / "index.html"] + sorted((ROOT / "assets").glob("*.html")) + sorted((ROOT / "demo").glob("*.html"))
    for path in files:
        findings = lint(path.read_text(encoding="utf-8"))
        p0 = [f for f in findings if f.severity == "P0"]
        ok = not p0
        print(f"  {'ok  ' if ok else 'FAIL'} {path.relative_to(ROOT)}")
        for f in p0:
            print(f"       P0 {f.id}: {f.message}")
        failures += 0 if ok else 1
    return failures


def main() -> int:
    failures = run_fixtures() + run_shipped()
    total = len(CASES) + 1 + len(list((ROOT / 'assets').glob('*.html'))) + len(list((ROOT / 'demo').glob('*.html')))
    print(f"\n{total - failures}/{total} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

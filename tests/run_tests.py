#!/usr/bin/env python3
"""
Design Studio lint + render self-tests.

Three suites:

1. Rule fixtures (tests/fixtures/*.html) — every rule must fire on a bad
   fixture and stay quiet on the good one.
2. Shipped artifacts (assets/*.html, demo/*.html) — the files we publish
   must lint with zero P0 findings.
3. Render verification — the shipped artifacts must also survive being
   rendered (no overflow, no clipped text, no contrast failure). Skipped
   when no Chrome/Chromium is available.

Run:  python3 tests/run_tests.py   (from the skill root)
Exit: 1 if any case fails.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from lint import lint  # noqa: E402
import verify  # noqa: E402
from compose import compose  # noqa: E402

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
    ("bad-mobile-grid.html", ["mobile-grid-1fr"], []),
    (
        "bad-agent.html",
        ["tool-call-missing-status", "destructive-without-approval", "stream-missing-aria-live",
         "run-missing-stop", "destructive-approve-unnamed", "tool-call-missing-output", "accent-overuse"],
        [],
    ),
    (
        "good-agent.html",
        [],
        ["tool-call-missing-status", "destructive-without-approval", "stream-missing-aria-live",
         "run-missing-stop", "destructive-approve-unnamed", "tool-call-missing-output", "accent-overuse"],
    ),
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
                missing.append(f"no-P0 (found {', '.join(p0)})")
        if name == "good-agent.html":
            p0 = [f.id for f in findings if f.severity == "P0"]
            if p0:
                missing.append(f"no-P0 (found {', '.join(p0)})")
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


FINDING_KEYS = {"severity", "id", "message", "fix", "snippet"}
V_FINDING_KEYS = {"severity", "id", "message", "fix", "selector", "detail", "viewports"}


def run_schema() -> int:
    """Pin docs/lint-schema-v1.md: every finding carries exactly the v1 keys."""
    print("· json schema v1")
    html = (FIXTURES / "bad-slop.html").read_text(encoding="utf-8")
    findings = lint(html)
    if not findings:
        print("  FAIL schema (fixture produced no findings)")
        return 1
    bad = [
        f"{f.id}:{sorted(vars(f).keys())}"
        for f in findings if set(vars(f).keys()) != FINDING_KEYS
    ]
    ok = not bad
    print(f"  {'ok  ' if ok else 'FAIL'} finding keys == {sorted(FINDING_KEYS)}")
    for b in bad:
        print(f"       {b}")
    return 0 if ok else 1


# ── render verification ───────────────────────────────────────────────────

VERIFY_VIEWPORTS = [(390, 844), (1440, 900)]

VERIFY_CASES = [
    (
        "good-render.html",
        [],
        ["overflow-x", "overflow-element", "text-clipped", "contrast-text",
         "runtime-error", "tap-target-small", "img-missing-dimensions",
         "focus-style-missing", "viewport-meta-missing"],
    ),
    (
        "bad-render.html",
        ["overflow-x", "overflow-element", "text-clipped", "contrast-text",
         "runtime-error", "tap-target-small", "img-missing-dimensions",
         "focus-style-missing", "viewport-meta-missing"],
        [],
    ),
]


def run_verify_fixtures(chrome: str) -> int:
    failures = 0
    print("· render fixtures")
    for name, must, must_not in VERIFY_CASES:
        path = FIXTURES / name
        vf = verify.verify_file(path, chrome, VERIFY_VIEWPORTS, 45, None)
        ids = {f.id for f in vf.findings}
        missing = [i for i in must if i not in ids]
        extra = [i for i in must_not if i in ids]
        ok = not missing and not extra
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
        if missing:
            print(f"       missing expected: {', '.join(missing)}")
        if extra:
            print(f"       unexpected: {', '.join(extra)}")
        failures += 0 if ok else 1
    return failures


def run_verify_shipped(chrome: str) -> int:
    """Every published artifact must render clean at mobile and desktop."""
    failures = 0
    print("· render: shipped artifacts (zero P0/P1 required)")
    files = [ROOT / "index.html"] + sorted((ROOT / "assets").glob("*.html")) \
        + sorted((ROOT / "demo").glob("*.html"))
    for path in files:
        vf = verify.verify_file(path, chrome, VERIFY_VIEWPORTS, 45, None)
        if vf.skipped:
            print(f"  ok   {path.relative_to(ROOT)} — {vf.skipped}")
            continue
        bad = [f for f in vf.findings if f.severity in ("P0", "P1")]
        ok = not bad and not vf.error
        print(f"  {'ok  ' if ok else 'FAIL'} {path.relative_to(ROOT)}")
        if vf.error:
            print(f"       {vf.error}")
        for f in bad:
            print(f"       {f.severity} {f.id}: {f.message}")
        failures += 0 if ok else 1
    return failures


def run_verify_composed(chrome: str) -> int:
    """The paste-ready section library must survive being pasted in."""
    failures = 0
    print("· render: composed section library")
    seed = ROOT / "assets" / "prototype-seed.html"
    fragment = ROOT / "assets" / "section-skeletons.html"
    if not seed.is_file() or not fragment.is_file():
        print("  skip — seeds not found")
        return 0
    with tempfile.TemporaryDirectory(prefix="design-studio-compose.") as tmp:
        out = Path(tmp) / "composed.html"
        out.write_text(
            compose(seed.read_text(encoding="utf-8"),
                    fragment.read_text(encoding="utf-8")),
            encoding="utf-8",
        )
        vf = verify.verify_file(out, chrome, VERIFY_VIEWPORTS, 45, None)
        bad = [f for f in vf.findings if f.severity in ("P0", "P1")]
        ok = not bad and not vf.error
        print(f"  {'ok  ' if ok else 'FAIL'} prototype-seed + section-skeletons")
        if vf.error:
            print(f"       {vf.error}")
        for f in bad:
            print(f"       {f.severity} {f.id}: {f.message}")
        failures += 0 if ok else 1
    return failures


def run_verify_schema(chrome: str) -> int:
    """Pin docs/verify-schema-v1.md: the render finding shape is frozen."""
    print("· verify json schema v1")
    path = FIXTURES / "bad-render.html"
    vf = verify.verify_file(path, chrome, VERIFY_VIEWPORTS, 45, None)
    if not vf.findings:
        print("  FAIL schema (fixture produced no findings)")
        return 1
    bad = [
        f"{f.id}:{sorted(vars(f).keys())}"
        for f in vf.findings if set(vars(f).keys()) != V_FINDING_KEYS
    ]
    ok = not bad
    print(f"  {'ok  ' if ok else 'FAIL'} finding keys == {sorted(V_FINDING_KEYS)}")
    for b in bad:
        print(f"       {b}")
    return 0 if ok else 1


def run_verify() -> int:
    chrome = verify.find_chrome()
    if not chrome:
        print("· render verification — skipped (no Chrome/Chromium found)")
        return 0
    return (
        run_verify_fixtures(chrome)
        + run_verify_shipped(chrome)
        + run_verify_composed(chrome)
        + run_verify_schema(chrome)
    )


def main() -> int:
    failures = run_fixtures() + run_shipped() + run_schema()
    total = len(CASES) + 2 + len(list((ROOT / 'assets').glob('*.html'))) \
        + len(list((ROOT / 'demo').glob('*.html')))
    failures += run_verify()
    total += 4
    print(f"\n{total - failures}/{total} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

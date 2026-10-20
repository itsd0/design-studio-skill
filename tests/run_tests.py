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

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from lint import lint  # noqa: E402
import verify  # noqa: E402
import pngread  # noqa: E402
import contract as contract_mod  # noqa: E402
import extract as extract_mod  # noqa: E402
import directions as directions_mod  # noqa: E402
import score as score_mod  # noqa: E402
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


# ── contract fidelity ─────────────────────────────────────────────────────


def run_contract() -> int:
    """The contract checker must catch drift, and accept a matching artifact."""
    failures = 0
    print("· contract fidelity")

    seed = ROOT / "demo" / "landing.html"
    design = ROOT / "demo" / "design.md"
    if not seed.is_file() or not design.is_file():
        print("  skip — demo files not found")
        return 0

    html = seed.read_text(encoding="utf-8")
    contract = contract_mod.parse_contract(design.read_text(encoding="utf-8"), str(design))

    # The demo artifact must satisfy its own contract.
    findings = contract_mod.check(contract, html, str(seed))
    p0 = [f for f in findings if f.severity == "P0"]
    ok = not p0
    print(f"  {'ok  ' if ok else 'FAIL'} demo/landing.html matches demo/design.md")
    for f in p0:
        print(f"       P0 {f.id}: {f.message}")
    failures += 0 if ok else 1

    # A drifted token must be a P0.
    drifted = html.replace("--accent:", "--accent: #ff0000;", 1)
    if drifted != html:
        drift_findings = contract_mod.check(contract, drifted, "drifted.html")
        ids = {f.id for f in drift_findings}
        ok = "design-md-token-drift" in ids
        print(f"  {'ok  ' if ok else 'FAIL'} a drifted token is reported")
        if not ok:
            print(f"       expected design-md-token-drift, got {sorted(ids)}")
        failures += 0 if ok else 1

    # A missing token must be a P0.
    missing = re.sub(r"--accent:[^;]+;", "", html, count=1)
    if missing != html:
        ids = {f.id for f in contract_mod.check(contract, missing, "missing.html")}
        ok = "design-md-token-missing" in ids
        print(f"  {'ok  ' if ok else 'FAIL'} a missing token is reported")
        if not ok:
            print(f"       expected design-md-token-missing, got {sorted(ids)}")
        failures += 0 if ok else 1

    return failures


# ── design system extraction ──────────────────────────────────────────────


def run_extract() -> int:
    """Extraction must round-trip: the tokens it reads back must be the ones
    the artifact actually uses."""
    failures = 0
    print("· design system extraction")
    chrome = verify.find_chrome()
    if not chrome:
        print("  skip — no Chrome/Chromium found")
        return 0

    target = ROOT / "index.html"
    raw = target.read_text(encoding="utf-8")
    result = extract_mod.extract_from_page(raw, chrome, str(target))
    tokens = result["tokens"]

    # Compare the extracted tokens with the ones the artifact declares.
    declared = {}
    for m in re.finditer(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", raw):
        declared[m.group(1)] = m.group(2).strip()

    def close(name: str) -> bool:
        want = declared.get(name)
        if not want:
            return True
        a = extract_mod.to_rgb(want)
        b = extract_mod.to_rgb(tokens.get(name, ""))
        if not a or not b:
            return want.strip() == tokens.get(name, "").strip()
        return all(abs(x - y) <= 6 for x, y in zip(a, b))

    for name in ("--bg", "--fg", "--accent"):
        ok = close(name)
        print(f"  {'ok  ' if ok else 'FAIL'} {name} round-trips "
              f"({declared.get(name, '?')} → {tokens.get(name, '?')})")
        failures += 0 if ok else 1

    # The contract it writes must be complete enough for the checker.
    with tempfile.TemporaryDirectory(prefix="design-studio-extract-test.") as tmp:
        out = Path(tmp)
        (out / "DESIGN.md").write_text(
            extract_mod.design_md(result, "Test"), encoding="utf-8")
        (out / "tokens.css").write_text(
            extract_mod.tokens_css(result), encoding="utf-8")
        parsed = contract_mod.parse_contract(
            (out / "DESIGN.md").read_text(encoding="utf-8"), "DESIGN.md")
        ok = len(parsed.tokens) >= 6 and "--font-display" in parsed.fonts
        print(f"  {'ok  ' if ok else 'FAIL'} the written contract parses back "
              f"({len(parsed.tokens)} tokens)")
        failures += 0 if ok else 1

    return failures


# ── directions ────────────────────────────────────────────────────────────


def run_directions() -> int:
    """The direction studio must produce distinct candidates, and render."""
    failures = 0
    print("· direction studio")

    candidates = directions_mod.generate("AI infrastructure for autonomous agents", 3)
    ok = len(candidates) == 3
    print(f"  {'ok  ' if ok else 'FAIL'} three candidates from a brief")
    failures += 0 if ok else 1

    accents = {c["tokens"]["--accent"] for c in candidates}
    bgs = {c["tokens"]["--bg"] for c in candidates}
    ok = len(accents) == 3 and len(bgs) == 3
    print(f"  {'ok  ' if ok else 'FAIL'} the candidates are visually distinct")
    if not ok:
        print(f"       accents {sorted(accents)}")
    failures += 0 if ok else 1

    # A different brief must not return the same winner.
    other = directions_mod.generate("editorial newsletter for a research lab", 1)
    ok = other[0]["id"] != candidates[0]["id"]
    print(f"  {'ok  ' if ok else 'FAIL'} a different brief picks a different direction")
    failures += 0 if ok else 1

    chrome = verify.find_chrome()
    if not chrome:
        print("  skip — comparison sheet (no Chrome)")
        return failures
    with tempfile.TemporaryDirectory(prefix="design-studio-dir-test.") as tmp:
        out = Path(tmp) / "sheet.png"
        ok = directions_mod.render_sheet(candidates, "test", out)
        size = pngread.png_size(out) if out.exists() else None
        print(f"  {'ok  ' if ok and size else 'FAIL'} the comparison sheet renders "
              f"({size[0]}×{size[1] if size else 0})")
        failures += 0 if (ok and size) else 1

    return failures


# ── craft scorecard ───────────────────────────────────────────────────────


def run_score() -> int:
    """The scorecard must pass a good artifact and catch a broken one."""
    failures = 0
    print("· craft scorecard")
    chrome = verify.find_chrome()
    if not chrome:
        print("  skip — no Chrome/Chromium found")
        return 0

    target = ROOT / "index.html"
    raw = target.read_text(encoding="utf-8")
    data = score_mod.collect(raw, chrome)
    if not data:
        print("  FAIL could not render the artifact")
        return 1

    checks = score_mod.build_checks(data, raw)
    failed = [c.id for c in checks if c.ok is False]
    # The landing page is a flagship artifact: nothing should fail.
    ok = not failed
    print(f"  {'ok  ' if ok else 'FAIL'} index.html passes every craft check")
    for c in checks:
        if c.ok is False:
            print(f"       {c.id}: {c.detail}")
    failures += 0 if ok else 1

    distance = data.get("defaultDistance", {})
    ok = 0 <= distance.get("score", -1) <= 4
    print(f"  {'ok  ' if ok else 'FAIL'} the default-distance score is in range "
          f"({distance.get('score')}/4)")
    failures += 0 if ok else 1

    return failures


# ── MCP server ────────────────────────────────────────────────────────────


# ── design DNA library ────────────────────────────────────────────────────


LIBRARY_SECTIONS = ["Use it for", "Tokens", "Anti-patterns"]


def run_library() -> int:
    """Every design-DNA entry must be complete and contrast-safe."""
    failures = 0
    print("· design DNA library")
    lib = ROOT / "references" / "library"
    entries = sorted(p for p in lib.glob("*.md") if p.name != "README.md")
    ok = len(entries) >= 18
    print(f"  {'ok  ' if ok else 'FAIL'} {len(entries)} entries (18 required)")
    failures += 0 if ok else 1

    for path in entries:
        text = path.read_text(encoding="utf-8")
        missing = [s for s in LIBRARY_SECTIONS if s not in text]
        tokens = contract_mod.parse_root_tokens(text)
        problems = []
        if missing:
            problems.append(f"missing sections: {', '.join(missing)}")
        if len(tokens) < 6:
            problems.append(f"only {len(tokens)} tokens")

        # Core pairs must pass the same contrast the artifacts do.
        def rgb(name):
            value = tokens.get(name, "")
            return extract_mod.to_rgb(value) if value else None

        bg, fg = rgb("--bg"), rgb("--fg")
        accent, accent_on = rgb("--accent"), rgb("--accent-on")
        if bg and fg and extract_mod.contrast(fg, bg) < 4.5:
            problems.append(f"fg/bg {extract_mod.contrast(fg, bg):.1f}:1")
        if bg and tokens.get("--muted"):
            muted = rgb("--muted")
            if muted and extract_mod.contrast(muted, bg) < 4.5:
                problems.append(f"muted/bg {extract_mod.contrast(muted, bg):.1f}:1")
        if accent and accent_on and extract_mod.contrast(accent_on, accent) < 4.5:
            problems.append(f"accent-on/accent {extract_mod.contrast(accent_on, accent):.1f}:1")

        good = not problems
        print(f"  {'ok  ' if good else 'FAIL'} {path.stem}")
        for p in problems:
            print(f"       {p}")
        failures += 0 if good else 1

    return failures


# ── handoff + review ──────────────────────────────────────────────────────


def run_handoff() -> int:
    """The handoff spec must carry the tokens, sections and acceptance checks."""
    failures = 0
    print("· handoff spec")
    import handoff as handoff_mod

    artifact = ROOT / "demo" / "landing.html"
    design = ROOT / "demo" / "design.md"
    spec = handoff_mod.build(artifact, design)
    text = handoff_mod.render(spec)

    for needle, label in (
        ("## Design tokens", "token table"),
        ("## Page inventory", "page inventory"),
        ("## Accessibility contract", "accessibility contract"),
        ("## Acceptance checks", "acceptance checks"),
        ("--accent", "accent token"),
    ):
        ok = needle in text
        print(f"  {'ok  ' if ok else 'FAIL'} handoff includes {label}")
        failures += 0 if ok else 1

    ok = len(spec["sections"]) >= 4 and len(spec["tokens"]) >= 8
    print(f"  {'ok  ' if ok else 'FAIL'} handoff reads the artifact "
          f"({len(spec['sections'])} sections, {len(spec['tokens'])} tokens)")
    failures += 0 if ok else 1
    return failures


def run_review() -> int:
    """The review document must run every gate and reach the right verdict."""
    failures = 0
    print("· review document")
    chrome = verify.find_chrome()
    if not chrome:
        print("  skip — no Chrome/Chromium found")
        return 0

    import review as review_mod

    artifact = ROOT / "demo" / "landing.html"
    report = review_mod.collect(artifact, chrome, None)
    text = review_mod.render(report, None)

    ok = "**Verdict: PASS" in text
    print(f"  {'ok  ' if ok else 'FAIL'} a clean artifact passes review")
    failures += 0 if ok else 1

    gates = {f["gate"] for f in report["findings"]}
    ok = "source" in gates or "contract" in gates or not report["findings"]
    print(f"  {'ok  ' if ok else 'FAIL'} every gate reports ({', '.join(sorted(gates)) or 'clean'})")
    failures += 0 if ok else 1

    ok = "## Craft scorecard" in text and "## Judgement checklist" in text
    print(f"  {'ok  ' if ok else 'FAIL'} the review carries the scorecard and the checklist")
    failures += 0 if ok else 1

    return failures


def run_skill_md() -> int:
    """SKILL.md must match the Agent Skills authoring rules."""
    print("· skill file spec")
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tests" / "test_skill_md.py")],
        capture_output=True, text=True, timeout=120,
    )
    for line in proc.stdout.splitlines():
        if line.startswith("  "):
            print(line)
    return 0 if proc.returncode == 0 else 1


def run_mcp() -> int:
    """The MCP server must answer initialize, tools/list and tools/call."""
    failures = 0
    print("· mcp server")
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05", "capabilities": {}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "design_studio_lint",
                    "arguments": {"path": str(ROOT / "tests" / "fixtures" / "bad-slop.html")}}},
    ]
    payload = "\n".join(json.dumps(r) for r in requests) + "\n"
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "mcp_server.py")],
        input=payload, capture_output=True, text=True, timeout=120,
    )
    responses = {}
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        if "id" in msg:
            responses[msg["id"]] = msg

    ok = 1 in responses and "result" in responses[1]
    print(f"  {'ok  ' if ok else 'FAIL'} initialize is answered")
    failures += 0 if ok else 1

    tools = responses.get(2, {}).get("result", {}).get("tools", [])
    names = {t["name"] for t in tools}
    expected = {"design_studio_lint", "design_studio_verify", "design_studio_contract",
                "design_studio_extract", "design_studio_score", "design_studio_directions"}
    ok = expected.issubset(names)
    print(f"  {'ok  ' if ok else 'FAIL'} every tool is advertised ({len(tools)})")
    if not ok:
        print(f"       missing {sorted(expected - names)}")
    failures += 0 if ok else 1

    content = responses.get(3, {}).get("result", {}).get("content", [])
    ok = bool(content) and "purple-gradient" in content[0].get("text", "")
    print(f"  {'ok  ' if ok else 'FAIL'} a tool call returns real output")
    failures += 0 if ok else 1
    return failures


def main() -> int:
    failures = run_fixtures() + run_shipped() + run_schema()
    total = len(CASES) + 2 + len(list((ROOT / 'assets').glob('*.html'))) \
        + len(list((ROOT / 'demo').glob('*.html')))
    failures += run_verify()
    total += 4
    failures += run_contract() + run_extract() + run_directions() + run_score() + run_mcp()
    total += 12
    failures += run_library() + run_handoff() + run_review() + run_skill_md()
    total += 25
    print(f"\n{total - failures}/{total} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

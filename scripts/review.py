#!/usr/bin/env python3
"""
Design Studio — review document.

Runs the four gates over an artifact and writes a review a team can post on
a pull request: a verdict, a findings table per gate, the craft scorecard,
screenshots, and the judgement checklist that still needs a human.

Usage:
    python3 scripts/review.py index.html
    python3 scripts/review.py index.html --out reviews/index.md --shots .shots
    python3 scripts/review.py index.html --json

Exit code 1 when a P0 finding exists.
"""

from __future__ import annotations

import json
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import contract as contract_mod  # noqa: E402
import lint as lint_mod  # noqa: E402
import score as score_mod  # noqa: E402
import verify as verify_mod  # noqa: E402

VIEWPORTS = [(390, 844), (768, 1024), (1440, 900)]


def as_row(severity: str, gate: str, ident: str, message: str, fix: str, where: str = "") -> dict:
    return {"severity": severity, "gate": gate, "id": ident,
            "message": message, "fix": fix, "where": where}


def collect(path: Path, chrome: str | None, shots: Path | None) -> dict:
    html = path.read_text(encoding="utf-8")

    lint_findings = [
        as_row(f.severity, "source", f.id, f.message, f.fix, f.snippet)
        for f in lint_mod.lint(html)
    ]

    verify_findings: list[dict] = []
    viewports: list[dict] = []
    if chrome:
        vf = verify_mod.verify_file(path, chrome, VIEWPORTS, 45, shots)
        for f in vf.findings:
            verify_findings.append(as_row(
                f.severity, "render", f.id, f.message, f.fix,
                f.selector or f.detail,
            ))
        viewports = vf.viewports
    else:
        verify_findings.append(as_row(
            "P1", "render", "render-skipped",
            "The render gate did not run — no Chrome/Chromium found.",
            "Run the review on a machine with Chrome to measure the rendered page.",
        ))

    contract_findings: list[dict] = []
    design = contract_mod.find_contract(path)
    if design:
        parsed = contract_mod.parse_contract(design.read_text(encoding="utf-8"), str(design))
        contract_findings = [
            as_row(f.severity, "contract", f.id, f.message, f.fix, f.detail)
            for f in contract_mod.check(parsed, html, str(path))
        ]

    score_checks: list[dict] = []
    distance = 0
    away: list[str] = []
    kind = "page"
    if chrome:
        data = score_mod.collect(html, chrome)
        if data:
            kind = data.get("kind", "page")
            score_checks = [c.as_dict() for c in score_mod.build_checks(data, html)]
            distance = data.get("defaultDistance", {}).get("score", 0)
            away = data.get("defaultDistance", {}).get("away", [])

    findings = lint_findings + verify_findings + contract_findings
    return {
        "artifact": str(path),
        "design": str(design) if design else "",
        "kind": kind,
        "findings": findings,
        "scorecard": score_checks,
        "distance": distance,
        "away": away,
        "viewports": viewports,
        "render_ran": bool(chrome),
    }


def counts(findings: list[dict]) -> dict:
    return {s: sum(1 for f in findings if f["severity"] == s) for s in ("P0", "P1", "P2")}


def render(report: dict, shots: Path | None) -> str:
    c = counts(report["findings"])
    passed = sum(1 for k in report["scorecard"] if k["ok"] is True)
    failed = [k for k in report["scorecard"] if k["ok"] is False]
    total = len(report["scorecard"])
    verdict = "FAIL — fix the P0 findings before shipping" if c["P0"] else (
        "PASS with advisories" if c["P1"] else "PASS")

    out = [
        f"# Design review — `{Path(report['artifact']).name}`",
        "",
        f"> {report['kind']} · reviewed {date.today().isoformat()} · "
        f"contract: `{report['design'] or '— none —'}`",
        "",
        f"**Verdict: {verdict}.**",
        "",
        f"| Gate | P0 | P1 | P2 |",
        "|---|---|---|---|",
    ]
    for gate in ("source", "render", "contract"):
        g = [f for f in report["findings"] if f["gate"] == gate]
        gc = counts(g)
        out.append(f"| {gate} | {gc['P0']} | {gc['P1']} | {gc['P2']} |")
    out.append(f"| **total** | **{c['P0']}** | **{c['P1']}** | **{c['P2']}** |")

    out += ["", "## Craft scorecard", ""]
    if total:
        out.append(f"**{passed}/{total} checks passed** · "
                   f"**{report['distance']}/4 away from the default look** "
                   f"({', '.join(report['away']) or 'matches the house style'}).")
        out += ["", "| Check | Result | Detail |", "|---|---|---|"]
        for k in report["scorecard"]:
            mark = "n/a" if k["ok"] is None else ("pass" if k["ok"] else "**FAIL**")
            out.append(f"| `{k['id']}` | {mark} | {k['detail']} |")
        if failed:
            out += ["", "**Fixes:**", ""]
            out += [f"- `{k['id']}` — {k['fix']}" for k in failed if k["fix"]]
    else:
        out.append("The scorecard did not run (it needs a browser).")

    if report["viewports"]:
        out += ["", "## Rendered viewports", ""]
        out += ["| Viewport | Layout | Content | Elements |", "|---|---|---|---|"]
        for vp in report["viewports"]:
            m, d = vp.get("measured", {}), vp.get("doc", {})
            out.append(f"| {vp['viewport']} | {m.get('w')}px | "
                       f"{d.get('scrollWidth')}px | {vp.get('counts', {}).get('elements', 0)} |")
        if shots:
            out += ["", "Screenshots:"]
            for png in sorted(Path(shots).glob("*.png")):
                out.append(f"- `{png}`")

    if report["findings"]:
        out += ["", "## Findings", "", "Ordered P0 → P2. Each row names the gate, the rule and the fix.", ""]
        out += ["| Sev | Gate | Rule | Where | What | Fix |", "|---|---|---|---|---|---|"]
        for f in sorted(report["findings"], key=lambda f: ("P0", "P1", "P2").index(f["severity"])):
            where = f["where"].replace("|", "\\|")[:60]
            message = f["message"].replace("|", "\\|")[:110]
            fix = f["fix"].replace("|", "\\|")[:110]
            out.append(f"| {f['severity']} | {f['gate']} | `{f['id']}` | `{where}` | {message} | {fix} |")
    else:
        out += ["", "## Findings", "", "No findings. The gates are clean."]

    out += [
        "", "## Judgement checklist", "",
        "The gates measure mechanics. These still need a human, in this order:",
        "",
        "- [ ] **Claim** — can you say the page's one sentence after the headline?",
        "- [ ] **Hierarchy** — does the eye land on the claim, then the action, then the evidence?",
        "- [ ] **Accent** — can you point at the accent in one breath?",
        "- [ ] **Surface** — structure, not floating cards?",
        "- [ ] **Evidence** — does it show the product working, or describe it?",
        "- [ ] **States** — loading, empty and error on every stateful surface?",
        "- [ ] **Rhythm** — dense and open alternating, not one uniform weight?",
        "- [ ] **Distance** — would you recognise this as *this* product's page?",
        "- [ ] **Handoff** — could someone else ship this from `HANDOFF.md`?",
        "",
        "The worked examples for each step live in `references/critique.md`.",
        "",
        "## Reproduce", "",
        "```bash",
        f"python3 scripts/lint.py {report['artifact']}",
        f"python3 scripts/verify.py {report['artifact']}",
        f"python3 scripts/contract.py {report['artifact']}",
        f"python3 scripts/score.py {report['artifact']}",
        "```",
        "",
    ]
    return "\n".join(out)


def main(argv: list[str]) -> int:
    as_json = "--json" in argv
    out_path = None
    shots = None
    artifact = None
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--out":
            i += 1
            out_path = Path(argv[i]) if i < len(argv) else None
        elif a == "--shots":
            i += 1
            shots = Path(argv[i]) if i < len(argv) else None
        elif not a.startswith("-"):
            artifact = Path(a)
        i += 1

    if not artifact or not artifact.is_file():
        print(__doc__.strip())
        return 2

    chrome = verify_mod.find_chrome()
    report = collect(artifact, chrome, shots)

    if as_json:
        print(json.dumps(report, indent=2))
    else:
        text = render(report, shots)
        target = out_path or artifact.parent / f"REVIEW-{artifact.stem}.md"
        target.write_text(text, encoding="utf-8")
        c = counts(report["findings"])
        print(f"review · {artifact}")
        print(f"  wrote {target}")
        print(f"  {c['P0']} P0 · {c['P1']} P1 · {c['P2']} P2 · "
              f"{report['distance']}/4 from the default")
        print(f"  {'FAIL' if c['P0'] else 'pass'}")

    return 1 if counts(report["findings"])["P0"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

#!/usr/bin/env python3
"""
Design Studio — handoff spec.

The artifact is the design step; a framework is the build step. This tool
turns an approved artifact into a spec another engineer (or another agent)
can implement without guessing: tokens, type, page inventory, components,
states, breakpoints, the accessibility contract, and the acceptance checks.

Usage:
    python3 scripts/handoff.py index.html
    python3 scripts/handoff.py index.html --out HANDOFF.md
    python3 scripts/handoff.py index.html --design ./DESIGN.md --json
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import contract as contract_mod  # noqa: E402

COMPONENT_HINTS = {
    "btn": "button",
    "field": "form field",
    "card": "card",
    "panel": "panel",
    "app-window": "app / studio window",
    "app-bar": "window chrome",
    "app-pane": "window pane",
    "bento-hairline": "bento grid",
    "bento-cell": "bento cell",
    "bento-visual": "schematic stage",
    "index-showcase": "indexed showcase",
    "tablewrap": "table scroll container",
    "tabs": "tabs",
    "tab": "tab",
    "modal": "modal",
    "toast": "toast",
    "skeleton": "skeleton",
    "empty": "empty state",
    "toolbar": "toolbar",
    "rail": "side rail",
    "kpi": "KPI",
    "chart": "chart",
    "pill": "status pill",
    "badge": "badge",
    "tag": "tag",
    "code": "code block",
}

STATE_PATTERNS = {
    "hover": r":hover",
    "focus-visible": r":focus-visible",
    "active": r":active",
    "disabled": r":disabled|\[disabled\]",
    "aria-current": r'aria-current="[^"]+"',
    "aria-busy": r'aria-busy="[^"]+"',
    "error state": r"\.is-error|aria-invalid",
    "loading state": r"\.skeleton|aria-busy",
    "empty state": r"\.empty\b",
    "reduced motion": r"prefers-reduced-motion",
}


def strip_tags(html: str) -> str:
    import html as html_mod
    text = re.sub(r"<[^>]+>", " ", html)
    text = html_mod.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def page_inventory(html: str) -> list[dict]:
    out = []
    for m in re.finditer(r'<section\b([^>]*)>([\s\S]*?)</section>', html, re.I):
        attrs, inner = m.group(1), m.group(2)
        did = re.search(r'data-design-id="([^"]+)"', attrs)
        label = re.search(r'data-screen-label="([^"]+)"', attrs)
        heading = re.search(r"<h[1-3][^>]*>([\s\S]*?)</h[1-3]>", inner, re.I)
        out.append({
            "id": did.group(1) if did else (label.group(1) if label else ""),
            "heading": strip_tags(heading.group(1))[:80] if heading else "",
            "components": sorted({
                c for c in re.findall(r'class="([^"]+)"', inner)
                for c in c.split()
                if c in COMPONENT_HINTS
            }),
            "words": len(strip_tags(inner).split()),
        })
    return out


def component_inventory(html: str) -> list[dict]:
    counts: Counter = Counter()
    for m in re.finditer(r'class="([^"]+)"', html):
        for cls in m.group(1).split():
            counts[cls] += 1
    out = []
    for cls, count in counts.most_common():
        if cls in COMPONENT_HINTS:
            out.append({"class": cls, "role": COMPONENT_HINTS[cls], "count": count})
    return out


def states(html: str) -> list[str]:
    found = []
    for label, pattern in STATE_PATTERNS.items():
        if re.search(pattern, html, re.I):
            found.append(label)
    return found


def breakpoints(html: str) -> list[str]:
    values = set()
    for m in re.finditer(r"@media\s*\(([^)]*max-width[^)]*)\)", html, re.I):
        px = re.search(r"(\d+)px", m.group(1))
        if px:
            values.add(f"≤ {px.group(1)}px")
    return sorted(values, key=lambda v: -int(re.findall(r"\d+", v)[0]))


def a11y_facts(html: str) -> dict:
    return {
        "h1": len(re.findall(r"<h1\b", html, re.I)),
        "headings": len(re.findall(r"<h[1-6]\b", html, re.I)),
        "images": len(re.findall(r"<img\b", html, re.I)),
        "images_with_alt": len(re.findall(r"<img[^>]*\balt=", html, re.I)),
        "landmarks": sorted({
            t for t in re.findall(r"<(header|nav|main|footer|aside)\b", html, re.I)
        }),
        "labelled_controls": len(re.findall(r"aria-label=|aria-labelledby=|<label", html, re.I)),
        "focus_visible": bool(re.search(r":focus-visible|:focus\b", html, re.I)),
    }


def build(artifact: Path, design: Path | None) -> dict:
    html = artifact.read_text(encoding="utf-8")
    tokens = contract_mod.parse_root_tokens(html)
    contract = contract_mod.Contract()
    if design and design.is_file():
        contract = contract_mod.parse_contract(design.read_text(encoding="utf-8"), str(design))

    title = re.search(r"<title>([^<]+)</title>", html, re.I)
    kind = re.search(r'data-artifact="([^"]+)"', html)
    if not kind:
        kind = "deck" if re.search(r'class="slide\b', html) else "page"

    return {
        "artifact": str(artifact),
        "title": strip_tags(title.group(1)) if title else artifact.stem,
        "kind": kind if isinstance(kind, str) else kind.group(1),
        "design": str(design) if design else "",
        "tokens": tokens,
        "fonts": contract.fonts,
        "dials": contract.dials,
        "sections": page_inventory(html),
        "components": component_inventory(html),
        "states": states(html),
        "breakpoints": breakpoints(html),
        "a11y": a11y_facts(html),
        "lines": html.count("\n") + 1,
        "bytes": len(html.encode("utf-8")),
    }


def render(spec: dict) -> str:
    a = spec["a11y"]
    out = [
        f"# Handoff — {spec['title']}",
        "",
        f"> Artifact: `{spec['artifact']}` · kind: **{spec['kind']}** · "
        f"{spec['lines']} lines, {spec['bytes'] // 1024} KB",
        f"> Contract: `{spec['design'] or '— none —'}`",
        "",
        "This is the implementation spec for the approved artifact. The artifact is the",
        "visual source of truth; this file is what another engineer or agent needs to",
        "rebuild it in a framework without re-deciding the design.",
        "",
        "## Design tokens",
        "",
        "Bind these verbatim. Derived tones use `color-mix()`; no new hex values.",
        "",
        "| Token | Value |",
        "|---|---|",
    ]
    for name, value in spec["tokens"].items():
        if name.startswith("--"):
            out.append(f"| `{name}` | `{value}` |")

    if spec["fonts"]:
        out += ["", "## Typography", "", "| Role | Stack |", "|---|---|"]
        for name, value in spec["fonts"].items():
            out.append(f"| `{name}` | `{value}` |")

    if spec["dials"]:
        out += ["", "## Experience dials", ""]
        out += [f"- **{k.title()}:** `{v}`" for k, v in spec["dials"].items()]

    out += ["", "## Page inventory", ""]
    if spec["sections"]:
        out += ["| # | Anchor | Heading | Components | Words |", "|---|---|---|---|---|"]
        for i, s in enumerate(spec["sections"], start=1):
            out.append(
                f"| {i} | `{s['id']}` | {s['heading'] or '—'} | "
                f"{', '.join(f'`{c}`' for c in s['components']) or '—'} | {s['words']} |"
            )
    else:
        out.append("No `<section data-design-id>` elements — this artifact is not a page.")

    out += ["", "## Components", ""]
    if spec["components"]:
        out += ["| Class | Role | Occurrences |", "|---|---|---|"]
        for c in spec["components"]:
            out.append(f"| `.{c['class']}` | {c['role']} | {c['count']} |")
    else:
        out.append("No shared component classes found.")

    out += ["", "## States implemented", ""]
    out.append(", ".join(f"`{s}`" for s in spec["states"]) or "None found — add the missing states.")

    out += ["", "## Breakpoints", ""]
    out.append(", ".join(f"**{b}**" for b in spec["breakpoints"]) or "No media queries found.")

    out += [
        "", "## Accessibility contract", "",
        f"- `h1` elements: **{a['h1']}** (must stay exactly one)",
        f"- Headings: **{a['headings']}**",
        f"- Images: **{a['images']}**, with `alt`: **{a['images_with_alt']}**",
        f"- Landmarks: {', '.join(f'`<{l}>`' for l in a['landmarks']) or '—'}",
        f"- Labelled controls: **{a['labelled_controls']}**",
        f"- Visible focus: {'yes' if a['focus_visible'] else '**no**'}",
        "",
        "Preserve all of it. A framework port that loses the landmarks or the focus ring",
        "is a regression, not a port.",
    ]

    out += [
        "", "## Acceptance checks", "",
        "The port is done when these pass on the new implementation:",
        "",
        "```bash",
        "python3 scripts/lint.py <port>          # 0 P0",
        "python3 scripts/verify.py <port>        # 0 P0 at 390 / 768 / 1440",
        "python3 scripts/contract.py <port>      # 0 P0 against the same DESIGN.md",
        "python3 scripts/score.py <port>         # every check passes",
        "```",
        "",
        "If the framework swaps the font stack, re-run `score.py` and re-check the",
        "distance from the default — a framework default will pull it toward zero.",
        "",
        "## Notes for the implementer", "",
        "- Keep the token names. They are the contract, not a suggestion.",
        "- Replace `system-first` font stacks only with the product's real faces, and update `DESIGN.md` if you do.",
        "- Rebuild components with the framework's primitives, but keep the measured values: radius, padding, border width, font sizes.",
        "- Keep `data-design-id` on every section — it is how the next review points at things.",
        "- Copy is final unless the brief changes; do not paraphrase it during the port.",
        "",
    ]
    return "\n".join(out)


def main(argv: list[str]) -> int:
    as_json = "--json" in argv
    out_path = None
    design = None
    artifact = None
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--out":
            i += 1
            out_path = Path(argv[i]) if i < len(argv) else None
        elif a == "--design":
            i += 1
            design = Path(argv[i]) if i < len(argv) else None
        elif not a.startswith("-"):
            artifact = Path(a)
        i += 1

    if not artifact or not artifact.is_file():
        print(__doc__.strip())
        return 2

    if design is None:
        design = contract_mod.find_contract(artifact)

    spec = build(artifact, design)

    if as_json:
        print(json.dumps(spec, indent=2))
        return 0

    text = render(spec)
    target = out_path or artifact.parent / "HANDOFF.md"
    target.write_text(text, encoding="utf-8")
    print(f"handoff · {artifact}")
    print(f"  wrote {target}")
    print(f"  {len(spec['sections'])} sections · {len(spec['tokens'])} tokens · "
          f"{len(spec['components'])} components · {len(spec['breakpoints'])} breakpoints")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

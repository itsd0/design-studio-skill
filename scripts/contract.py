#!/usr/bin/env python3
"""
Design Studio — contract fidelity checker.

`DESIGN.md` is the brand contract: "bind :root verbatim, never invent
tokens". This tool makes that mechanical. It parses the contract and the
artifact's token block and reports the drift.

Usage:
    python3 scripts/contract.py index.html
    python3 scripts/contract.py index.html --design ./DESIGN.md
    python3 scripts/contract.py index.html --json

With no --design, DESIGN.md is looked up next to the artifact and then in
its parent directories.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract import contrast, hex_to_rgb, oklch_to_rgb, parse_css_color  # noqa: E402

SECTION_ORDER = [
    "Visual Theme & Atmosphere",
    "Experience Dials",
    "Color Palette & Roles",
    "Typography Rules",
    "Component Stylings",
    "Layout Principles",
    "Depth & Elevation",
    "Do's and Don'ts",
    "Responsive Behavior",
    "Agent Prompt Guide",
]

LABEL_TO_TOKEN = {
    "background": "--bg",
    "surface": "--surface",
    "surface-2": "--surface-2",
    "foreground": "--fg",
    "muted": "--muted",
    "border": "--border",
    "accent": "--accent",
    "accent-on": "--accent-on",
    "success": "--success",
    "warn": "--warn",
    "warning": "--warn",
    "danger": "--danger",
}

DIALS = ("density", "expressiveness", "motion")
DIAL_LEVELS = {
    "density": ("airy", "regular", "compact"),
    "expressiveness": ("restrained", "assured", "bold"),
    "motion": ("still", "standard", "lively"),
}


@dataclass
class VFinding:
    severity: str
    id: str
    message: str
    fix: str
    detail: str = ""


@dataclass
class Contract:
    path: str = ""
    sections: list[str] = field(default_factory=list)
    tokens: dict[str, str] = field(default_factory=dict)
    fonts: dict[str, str] = field(default_factory=dict)
    dials: dict[str, str] = field(default_factory=dict)


# ── parsing ───────────────────────────────────────────────────────────────


def parse_contract(text: str, path: str = "") -> Contract:
    c = Contract(path=path)

    # Sections, in the order they appear.
    for m in re.finditer(r"^##\s+(.+?)\s*$", text, re.M):
        c.sections.append(m.group(1).strip())

    # Colour tokens:  - **Background (`--bg`):** `value` — note
    #             or: - **Background:** `value` — note
    pattern = re.compile(
        r"^-\s*\*\*(?P<label>[A-Za-z0-9-]+)(?:\s*\(`(?P<token>[^`]+)`\))?\s*:\*\*\s*"
        r"`(?P<value>[^`]+)`",
        re.M,
    )
    for m in pattern.finditer(text):
        label = m.group("label").strip().lower()
        value = m.group("value").strip()
        token = m.group("token")
        if token:
            c.tokens[token.strip()] = value
        elif label in LABEL_TO_TOKEN:
            c.tokens[LABEL_TO_TOKEN[label]] = value

    # Typography:  - **Display / headings:** `stack`, weight 600
    for label, key in (("Display / headings", "--font-display"),
                       ("Body", "--font-body"),
                       ("Mono", "--font-mono")):
        m = re.search(r"^-\s*\*\*" + re.escape(label) + r":\*\*\s*`([^`]+)`", text, re.M)
        if m:
            c.fonts[key] = m.group(1).strip()

    # Dials:  - **Density:** `regular`
    for dial in DIALS:
        m = re.search(r"^-\s*\*\*" + dial.title() + r":\*\*\s*`?([a-z]+)`?", text, re.M | re.I)
        if m:
            c.dials[dial] = m.group(1).lower()

    return c


def parse_root_tokens(html: str) -> dict[str, str]:
    """The artifact's :root token block."""
    tokens: dict[str, str] = {}
    for m in re.finditer(r":root\s*\{(.*?)\}", html, re.S):
        block = m.group(1)
        for decl in re.finditer(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", block, re.I):
            tokens[decl.group(1).strip()] = decl.group(2).strip()
    return tokens


def to_rgb(value: str) -> tuple[int, int, int] | None:
    v = value.strip()
    if v.startswith("oklch("):
        m = re.fullmatch(
            r"oklch\(\s*([\d.]+%?)\s+([\d.]+)\s+([\d.]+)(?:deg)?\s*\)", v, re.I
        )
        if m:
            raw_l = m.group(1)
            try:
                L = float(raw_l.rstrip("%")) / (100 if raw_l.endswith("%") else 1)
            except ValueError:
                return None
            return oklch_to_rgb(L, float(m.group(2)), float(m.group(3)))
        return None
    if v.startswith("#"):
        return hex_to_rgb(v)
    return parse_css_color(v)


def values_equal(a: str, b: str) -> bool:
    """Equal as strings, or equal as colours (any notation)."""
    if a.strip() == b.strip():
        return True
    ra, rb = to_rgb(a), to_rgb(b)
    if ra and rb:
        return all(abs(x - y) <= 2 for x, y in zip(ra, rb))
    return False


# ── checking ──────────────────────────────────────────────────────────────


def check(contract: Contract, html: str, artifact: str) -> list[VFinding]:
    out: list[VFinding] = []

    if not contract.path:
        out.append(VFinding(
            "P1", "design-md-missing",
            "No DESIGN.md contract found — the artifact's tokens cannot be verified.",
            "Add a DESIGN.md beside the artifact (or pass --design) so the brand contract "
            "is the source of truth.",
        ))
        return out

    root = parse_root_tokens(html)
    if not root:
        out.append(VFinding(
            "P0", "design-md-no-tokens",
            "The artifact has no :root token block — it cannot bind the contract.",
            "Bind the contract's tokens verbatim in a single :root block.",
        ))
        return out

    # Tokens the contract declares must exist and match.
    for name, value in contract.tokens.items():
        if name not in root:
            out.append(VFinding(
                "P0", "design-md-token-missing",
                f"`{name}` is in the contract (`{value}`) but not in the artifact's :root.",
                f"Add `{name}: {value};` to the token block — the contract is the source of truth.",
                detail=name,
            ))
            continue
        if not values_equal(root[name], value):
            out.append(VFinding(
                "P0", "design-md-token-drift",
                f"`{name}` is `{root[name]}` in the artifact but `{value}` in the contract.",
                f"Set `{name}` back to the contract value — an artifact must not drift from its brand.",
                detail=name,
            ))

    # Fonts.
    for name, value in contract.fonts.items():
        if name not in root:
            out.append(VFinding(
                "P1", "design-md-font-missing",
                f"`{name}` is in the contract but not bound in the artifact.",
                f"Bind `{name}: {value};` in the token block.",
                detail=name,
            ))
        elif not values_equal(root[name], value):
            out.append(VFinding(
                "P1", "design-md-font-drift",
                f"`{name}` is `{root[name]}` in the artifact but `{value}` in the contract.",
                f"Set `{name}` back to the contract stack.",
                detail=name,
            ))

    # Contract completeness: required sections, in order.
    present = [s for s in SECTION_ORDER if any(
        s.lower() in got.lower() for got in contract.sections)]
    missing = [s for s in SECTION_ORDER if s not in present]
    if missing:
        out.append(VFinding(
            "P1", "design-md-section-missing",
            f"The contract is missing required section(s): {', '.join(missing)}.",
            "Every contract carries the required sections in order — an agent reads the whole file.",
            detail=", ".join(missing),
        ))

    order = [SECTION_ORDER.index(s) for s in present]
    if order != sorted(order):
        out.append(VFinding(
            "P1", "design-md-order-mismatch",
            "The contract's sections are not in the required order.",
            "Order the sections as the contract shape specifies: "
            + " → ".join(SECTION_ORDER),
        ))

    # Dials.
    for dial in DIALS:
        if dial not in contract.dials:
            out.append(VFinding(
                "P1", "design-md-dial-missing",
                f"The {dial} dial is not recorded in the contract.",
                f"Record it — {dial} is one of {'/'.join(DIAL_LEVELS[dial])}.",
                detail=dial,
            ))
        elif contract.dials[dial] not in DIAL_LEVELS[dial]:
            out.append(VFinding(
                "P1", "design-md-dial-invalid",
                f"The {dial} dial is `{contract.dials[dial]}`, which is not a level.",
                f"Use one of {'/'.join(DIAL_LEVELS[dial])}.",
                detail=dial,
            ))

    # Extra tokens the contract never declared (informational).
    declared = set(contract.tokens) | set(contract.fonts)
    extra = sorted(n for n in root if n not in declared)
    if extra:
        out.append(VFinding(
            "P2", "design-md-token-extra",
            f"{len(extra)} token(s) are not declared in the contract: {', '.join(extra[:8])}"
            + ("…" if len(extra) > 8 else ""),
            "Derived tokens are fine, but a raw colour outside the contract is an invented value.",
            detail=", ".join(extra[:8]),
        ))

    return out


def find_contract(artifact: Path) -> Path | None:
    for base in (artifact.parent, artifact.parent.parent, Path.cwd()):
        for name in ("DESIGN.md", "design.md"):
            candidate = base / name
            if candidate.is_file():
                return candidate
    return None


def main(argv: list[str]) -> int:
    as_json = "--json" in argv
    design_path = None
    files: list[str] = []
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--design":
            i += 1
            design_path = Path(argv[i]) if i < len(argv) else None
        elif not a.startswith("-"):
            files.append(a)
        i += 1

    if not files:
        print(__doc__.strip())
        return 2

    exit_code = 0
    for name in files:
        artifact = Path(name)
        if not artifact.is_file():
            print(f"contract · {name}\n  skipped — file not found\n")
            continue
        html = artifact.read_text(encoding="utf-8")

        dpath = design_path or find_contract(artifact)
        contract = Contract()
        if dpath and dpath.is_file():
            contract = parse_contract(dpath.read_text(encoding="utf-8"), str(dpath))
        else:
            contract.path = ""

        findings = check(contract, html, name)
        p0 = sum(1 for f in findings if f.severity == "P0")

        if as_json:
            print(json.dumps({
                "path": name,
                "design": contract.path or None,
                "counts": {
                    "P0": p0,
                    "P1": sum(1 for f in findings if f.severity == "P1"),
                    "P2": sum(1 for f in findings if f.severity == "P2"),
                },
                "findings": [
                    {"severity": f.severity, "id": f.id, "message": f.message,
                     "fix": f.fix, "detail": f.detail}
                    for f in findings
                ],
            }, indent=2))
        else:
            print(f"contract · {name}")
            print(f"  design: {contract.path or '— none found —'}")
            for f in findings:
                print(f"  [{f.severity}] {f.id} — {f.message}")
                print(f"        fix: {f.fix}")
            if not findings:
                print("  clean — the artifact matches its contract.")
            print(f"  {p0} P0 · {sum(1 for f in findings if f.severity == 'P1')} P1 · "
                  f"{sum(1 for f in findings if f.severity == 'P2')} P2 — "
                  f"{'FAIL' if p0 else 'pass'}\n")

        if p0:
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv))

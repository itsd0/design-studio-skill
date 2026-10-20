#!/usr/bin/env python3
"""
Validate SKILL.md against the Agent Skills authoring rules.

The skill file is the product: the agent decides whether to load it from the
description alone, and pays its full token cost on every run. This test keeps
it inside the budget and — more usefully — keeps every path it mentions real,
so the file cannot drift away from the repository.

Run:  python3 tests/test_skill_md.py
Exit: 1 if any check fails.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "SKILL.md"

REQUIRED_SECTIONS = [
    "Quick start",
    "Workflow checklist",
    "Workflow",
    "Gotchas",
    "Non-negotiables",
    "Load what you need",
    "When not to use",
]

# Long enough to be precise, short enough to load on every turn.
MAX_TOKENS = 5000
MAX_LINES = 500
MAX_DESCRIPTION = 1024
MAX_NAME = 64

PATH_RE = re.compile(r"`((?:references|assets|scripts|tests|docs|gallery)/[A-Za-z0-9_./<>-]+)`")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip()
    body = text[end + 4:]
    meta = {}
    for line in block.splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip()
    return meta, body


def main() -> int:
    failures = 0
    print("· skill file")

    if not SKILL.is_file():
        print("  FAIL SKILL.md not found")
        return 1

    text = SKILL.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    tokens = len(body) // 4
    lines = text.count("\n") + 1

    def check(ok: bool, label: str, detail: str = "") -> None:
        nonlocal failures
        print(f"  {'ok  ' if ok else 'FAIL'} {label}" + (f" ({detail})" if detail else ""))
        if not ok:
            failures += 1

    # ── frontmatter ──
    name = meta.get("name", "")
    check(bool(re.fullmatch(r"[a-z0-9-]{1,64}", name)), "name is valid",
          f"{name!r}")
    check("anthropic" not in name and "claude" not in name,
          "name avoids reserved words")

    description = meta.get("description", "")
    check(0 < len(description) <= MAX_DESCRIPTION, "description length",
          f"{len(description)}/{MAX_DESCRIPTION} chars")
    check("Use when" in description, "description names the triggers")
    check("Not for" in description, "description states the boundary")

    # ── budget ──
    check(tokens <= MAX_TOKENS, "body is within the token budget",
          f"{tokens}/{MAX_TOKENS} tokens (chars/4)")
    check(lines <= MAX_LINES, "body is within the line budget",
          f"{lines}/{MAX_LINES} lines")

    # ── structure ──
    headings = [h.strip() for h in re.findall(r"^##\s+(.+)$", body, re.M)]
    for section in REQUIRED_SECTIONS:
        check(any(h.startswith(section) for h in headings),
              f"section present: {section}")

    check("see references/ for details" not in body.lower(),
          "no generic 'see references/' hand-wave")

    # ── every path it names must exist ──
    missing = []
    for raw in sorted(set(PATH_RE.findall(text))):
        if "<" in raw or ">" in raw:
            continue  # a pattern, e.g. references/library/<id>.md
        if not (ROOT / raw).exists():
            missing.append(raw)
    check(not missing, "every referenced path exists",
          ", ".join(missing) if missing else "all resolve")

    # ── the load table must name the tools it ships ──
    scripts = sorted(p.name for p in (ROOT / "scripts").glob("*.py"))
    unnamed = [s for s in scripts if s not in ("__init__.py",) and s not in body]
    check(not unnamed, "every tool is documented in the skill file",
          ", ".join(unnamed) if unnamed else "all named")

    print()
    print(f"  {failures} failure(s)" if failures else "  skill file is within spec")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

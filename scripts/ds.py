#!/usr/bin/env python3
"""
Design Studio — one command for every gate.

    design-studio lint       <file>...        source gates
    design-studio verify     <file>...        render gates (headless Chrome)
    design-studio contract   <file>...        DESIGN.md ↔ artifact drift
    design-studio extract    <target>         URL / file / screenshot → DESIGN.md
    design-studio score      <file>...        craft scorecard
    design-studio directions --brief "..."    candidate directions + comparison sheet
    design-studio doctor                      check this machine's setup
    design-studio mcp                         run the MCP server on stdio

Every subcommand takes --json. `doctor` exits 0 when the toolchain is
usable and 1 when a required piece is missing.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

COMMANDS = {
    "lint": ("lint.py", "Anti-slop, token and accessibility gates over the source."),
    "verify": ("verify.py", "Render gates — overflow, clipping, contrast, tap targets."),
    "contract": ("contract.py", "DESIGN.md ↔ artifact drift."),
    "extract": ("extract.py", "Extract a design system into DESIGN.md + tokens.css."),
    "score": ("score.py", "Craft scorecard and distance from the default look."),
    "directions": ("directions.py", "Candidate directions from a brief; render a comparison sheet."),
}


def run(script: str, argv: list[str]) -> int:
    proc = subprocess.run([sys.executable, str(HERE / script), *argv])
    return proc.returncode


def doctor() -> int:
    print("design-studio · doctor\n")
    ok = True

    print(f"  python        {sys.version.split()[0]} — " +
          ("ok" if sys.version_info >= (3, 9) else "TOO OLD (need 3.9+)"))
    if sys.version_info < (3, 9):
        ok = False

    sys.path.insert(0, str(HERE))
    try:
        import verify
        chrome = verify.find_chrome()
    except Exception as exc:  # pragma: no cover
        chrome = None
        print(f"  chrome        could not be checked — {exc}")

    if chrome:
        print(f"  chrome        {chrome} — render gates available")
    else:
        print("  chrome        NOT FOUND — the render gate will report 'skipped'.")
        print("                 Install Chrome or Chromium to enable it.")

    for name in ("lint.py", "verify.py", "contract.py", "extract.py", "score.py",
                 "directions.py", "probe.js", "probe-design.js", "probe-score.js"):
        present = (HERE / name).is_file()
        print(f"  {name:<18}{'ok' if present else 'MISSING'}")
        if not present:
            ok = False

    refs = ROOT / "references"
    ref_files = list(refs.glob("*.md")) + list(refs.glob("library/*.md"))
    print(f"  references    {len(ref_files)} files — " +
          ("ok" if refs.is_dir() else "MISSING"))
    lib = refs / "library"
    print(f"  library       {len(list(lib.glob('*.md')))} design-DNA entries — " +
          ("ok" if lib.is_dir() else "MISSING"))

    print("\n  MCP:  claude mcp add design-studio -- python3 " + str(HERE / "mcp_server.py"))
    print("  npm:  npx design-studio doctor")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__.strip())
        return 2

    command = argv[1]
    rest = argv[2:]

    if command in ("-h", "--help", "help"):
        print(__doc__.strip())
        return 0
    if command == "doctor":
        return doctor()
    if command == "mcp":
        return run("mcp_server.py", rest)
    if command in COMMANDS:
        script, summary = COMMANDS[command]
        if not rest:
            print(f"design-studio {command} — {summary}\n")
            print(f"usage: design-studio {command} {script.replace('.py', '')} --help")
            return 2
        return run(script, rest)

    print(f"design-studio: unknown command '{command}'\n", file=sys.stderr)
    print(__doc__.strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

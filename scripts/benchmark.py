#!/usr/bin/env python3
"""
Design Studio — benchmark publisher.

Turns one brief into a published comparison page: the candidate directions
that were considered, rendered side by side, with the tokens each one
carries and the reasoning behind it.

The point of a benchmark is not to win — it is to make the method's
decisions visible. A reviewer can see which directions were considered, what
each one costs, and why the shipped one won.

Usage:
    python3 scripts/benchmark.py --brief "AI infrastructure for agents" \
        --out gallery/benchmarks/brief-01.html
"""

from __future__ import annotations

import base64
import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import directions as directions_mod  # noqa: E402
import score as score_mod  # noqa: E402
import verify  # noqa: E402

PAGE_CSS = """
*, *::before, *::after { box-sizing: border-box; }
html { color-scheme: dark; }
:root {
  --bg:        oklch(13% 0.006 255);
  --surface:   oklch(16% 0.008 255);
  --fg:        oklch(96% 0.004 255);
  --muted:     oklch(68% 0.012 255);
  --border:    oklch(24% 0.010 255);
  --accent:    oklch(80% 0.17 152);
  --accent-on: oklch(15% 0.02 152);
  --font-display: ui-serif, 'Iowan Old Style', 'Charter', Georgia, 'Times New Roman', serif;
  --font-body:    -apple-system, BlinkMacSystemFont, 'Inter', system-ui, sans-serif;
  --font-mono:    ui-monospace, 'SF Mono', Menlo, monospace;
}
body {
  margin: 0; background: var(--bg); color: var(--fg);
  font-family: var(--font-body);
  line-height: 1.55; -webkit-font-smoothing: antialiased;
}
code { font-family: var(--font-mono); font-size: .92em; }
.wrap { max-width: 1320px; margin-inline: auto; padding: 64px 32px 96px; }
.eyebrow { font-family: var(--font-mono); font-size: 11px;
  letter-spacing: .1em; text-transform: uppercase; color: var(--accent);
  margin: 0 0 18px; }
h1 { font-family: var(--font-display); font-size: clamp(30px, 4vw, 46px);
  line-height: 1.06; letter-spacing: -.028em; font-weight: 600; margin: 0 0 18px; }
.lead { color: var(--muted); font-size: 17px; max-width: 68ch; margin: 0 0 40px; }
h2 { font-family: var(--font-display); font-size: 22px; font-weight: 600;
  letter-spacing: -.02em; margin: 56px 0 8px; }
h2 + .sub { color: var(--muted); font-size: 14.5px; margin: 0 0 22px; max-width: 72ch; }
.brief { border: 1px solid var(--border); background: var(--surface);
  border-radius: 10px; padding: 20px 22px; font-size: 15px; color: var(--fg); }
.brief b { color: var(--accent); font-weight: 600; }
.sheet { border: 1px solid var(--border); border-radius: 12px; overflow: hidden;
  margin: 0 0 8px; background: var(--bg); }
.sheet img { display: block; width: 100%; height: auto; }
.grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 1px;
  background: var(--border); border: 1px solid var(--border);
  border-radius: 10px; overflow: hidden; margin-top: 32px; }
.cell { background: var(--surface); padding: 20px; }
.cell h3 { font-size: 15px; margin: 0 0 4px; font-weight: 600; }
.cell .why { color: var(--muted); font-size: 13px; margin: 0 0 14px; }
pre.tokens { font-family: var(--font-mono); font-size: 11.5px;
  line-height: 1.7; color: var(--fg); margin: 0; white-space: pre-wrap; }
table { width: 100%; border-collapse: collapse; font-size: 13.5px; margin-top: 8px; }
.tablewrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.tablewrap > table { min-width: 520px; }
th { text-align: left; font-family: var(--font-mono); font-size: 11px;
  letter-spacing: .06em; text-transform: uppercase; color: var(--muted);
  font-weight: 500; padding: 10px 14px; border-bottom: 1px solid var(--border); }
td { padding: 11px 14px; border-bottom: 1px solid var(--border);
  font-variant-numeric: tabular-nums; }
td .ok { color: var(--fg); }
footer { margin-top: 72px; padding-top: 24px; border-top: 1px solid var(--border);
  color: var(--muted); font-size: 13px; }
footer a { color: var(--accent); }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
@media (max-width: 920px) { .grid { grid-template-columns: minmax(0, 1fr); } }
"""


def b64_image(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def score_table(root: Path) -> str:
    """The craft scorecard of every shipped artifact, as a table."""
    chrome = verify.find_chrome()
    if not chrome:
        return "<p>Chrome is not available — the scorecard needs a browser to render.</p>"
    rows = []
    files = [root / "index.html"] + sorted((root / "demo").glob("*.html"))
    for path in files:
        if not path.is_file():
            continue
        try:
            raw = path.read_text(encoding="utf-8")
            data = score_mod.collect(raw, chrome)
        except Exception:
            continue
        if not data:
            continue
        checks = score_mod.build_checks(data, raw)
        passed = sum(1 for c in checks if c.ok)
        distance = data.get("defaultDistance", {}).get("score", 0)
        ok = passed == len(checks)
        rows.append(
            f"<tr><td>{path.relative_to(root)}</td>"
            f"<td>{'✓' if ok else '✗'} {passed}/{len(checks)}</td>"
            f"<td>{distance}/4</td>"
            f"<td>{', '.join(data.get('defaultDistance', {}).get('away', [])) or '—'}</td></tr>"
        )
    if not rows:
        return "<p>No artifact could be scored.</p>"
    return (
        '<div class="tablewrap"><table><thead><tr><th>Artifact</th><th>Checks</th>'
        "<th>From the default</th><th>What differs</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def build(brief: str, out: Path, root: Path) -> None:
    candidates = directions_mod.generate(brief, 3)
    with tempfile.TemporaryDirectory(prefix="design-studio-bench.") as tmp:
        sheet = Path(tmp) / "sheet.png"
        if not directions_mod.render_sheet(candidates, brief, sheet):
            raise SystemExit("benchmark: could not render the comparison sheet "
                             "(no Chrome?)")
        sheet_b64 = b64_image(sheet)

    cells = []
    for c in candidates:
        tokens = "\n".join(
            f"  {k}: {v};" for k, v in list(c["tokens"].items())[:7]
        )
        fonts = c["fonts"]["--font-display"]
        cells.append(
            f'<div class="cell"><h3>{c["name"]}</h3>'
            f'<p class="why">{c["why"]}</p>'
            f'<pre class="tokens">{tokens}</pre>'
            f'<pre class="tokens" style="margin-top:10px">'
            f'  --font-display: {fonts[:44]}…</pre>'
            f'<pre class="tokens" style="margin-top:4px">'
            f'  density: {c["density"]} · radius: {c["spacing"]["radius"]}</pre>'
            f"</div>"
        )

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Benchmark — {candidates[0]["name"]} and two others · Design Studio</title>
<style>{PAGE_CSS}</style>
</head>
<body>
<div class="wrap">
  <p class="eyebrow">Design Studio · benchmark 01</p>
  <h1>One brief, three directions, rendered side by side.</h1>
  <p class="lead">The method never picks a direction blind. It derives candidates from
  the brief, renders them, and lets a person choose. This page is the evidence —
  the same tools, the same gates, published.</p>

  <h2>The brief</h2>
  <p class="sub">Everything below was derived from these words. Nothing was chosen by taste.</p>
  <div class="brief"><b>{brief}</b></div>

  <h2>The candidates</h2>
  <p class="sub">Rendered with the same hero markup, so the only variable is the
  direction: palette, type voice, density.</p>
  <div class="sheet"><img alt="Three candidate directions rendered side by side" width="1440" height="620" src="data:image/png;base64,{sheet_b64}" /></div>
  <div class="grid">{''.join(cells)}</div>

  <h2>The gates these artifacts pass</h2>
  <p class="sub">A direction is only a candidate until it survives the render gate,
  the contract check and the craft scorecard. This is the scorecard for the
  artifacts in this repository.</p>
  {score_table(root)}

  <footer>
    Published with <a href="https://github.com/itsd0/design-studio-skill">Design Studio</a> —
    single-file HTML, no dependencies, no build step. Re-generate it with
    <code>python3 scripts/benchmark.py --brief "{brief}" --out gallery/benchmarks/brief-01.html</code>.
  </footer>
</div>
</body>
</html>
"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


def main(argv: list[str]) -> int:
    brief = ""
    out = Path("gallery/benchmarks/brief-01.html")
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--brief":
            i += 1
            brief = argv[i] if i < len(argv) else ""
        elif a == "--out":
            i += 1
            out = Path(argv[i]) if i < len(argv) else out
        i += 1
    if not brief:
        print(__doc__.strip())
        return 2
    root = Path(__file__).resolve().parent.parent
    build(brief, out, root)
    print(f"benchmark · wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

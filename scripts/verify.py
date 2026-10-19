#!/usr/bin/env python3
"""
Design Studio — render verification.

The linter (scripts/lint.py) reads source. This reads the *rendered*
artifact: it loads the page in headless Chrome, measures what a human
would actually see, and reports the things static analysis cannot see —
horizontal overflow, computed text contrast, clipped text, tap-target
size, runtime errors, missing image dimensions, focus indicators.

Usage:
    python3 scripts/verify.py artifact.html [more.html ...]
    python3 scripts/verify.py --json artifact.html
    python3 scripts/verify.py --screenshot .artifacts artifact.html

Options:
    --json               machine-readable output
    --screenshot DIR     write a PNG per viewport into DIR
    --viewports LIST     comma-separated WxH (default 390x844,768x1024,1440x900)
    --fail-on LEVEL      p0 (default) | p1 | p2 | none
    --timeout SECONDS    per-run timeout (default 45)
    --require-browser    exit 2 when no Chrome/Chromium is available
    --no-browser         skip rendering, exit 0

Exit status:
    0  no findings at or above --fail-on
    1  findings at or above --fail-on
    2  setup problem (no browser, unreadable file)

No dependencies beyond a Chrome/Chromium binary. Without one, the tool
degrades to "skipped" instead of failing — the skill still works offline.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBE = Path(__file__).resolve().parent / "probe.js"

DEFAULT_VIEWPORTS = [(390, 844), (768, 1024), (1440, 900)]
SEVERITY_ORDER = {"P0": 0, "P1": 1, "P2": 2}

CHROME_CANDIDATES = [
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "chrome",
    "msedge",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/snap/bin/chromium",
    "/usr/bin/microsoft-edge",
]


# ── findings ──────────────────────────────────────────────────────────────


@dataclass
class VFinding:
    severity: str  # P0 | P1 | P2
    id: str
    message: str
    fix: str
    selector: str = ""
    detail: str = ""
    viewports: list[str] = field(default_factory=list)

    def key(self) -> tuple:
        return (self.id, self.selector, self.detail)


@dataclass
class VFile:
    path: str
    viewports: list[dict] = field(default_factory=list)
    findings: list[VFinding] = field(default_factory=list)
    error: str = ""
    skipped: str = ""


# ── browser discovery ─────────────────────────────────────────────────────


def find_chrome() -> str | None:
    for cand in CHROME_CANDIDATES:
        if "/" in cand:
            p = Path(cand)
            if p.is_file() and os_access(p):
                return str(p)
            continue
        found = shutil.which(cand)
        if found:
            return found
    return None


def os_access(p: Path) -> bool:
    import os

    return os.access(str(p), os.X_OK)


def chrome_flags(tmp_profile: Path, dump: bool, screenshot: Path | None,
                 width: int, height: int) -> list[str]:
    flags = [
        "--headless=new",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        "--virtual-time-budget=6000",
        "--allow-file-access-from-files",
        f"--user-data-dir={tmp_profile}",
        f"--window-size={width},{height}",
    ]
    try:
        import os

        if hasattr(os, "geteuid") and os.geteuid() == 0:
            flags.append("--no-sandbox")
    except Exception:
        pass
    if dump:
        flags.append("--dump-dom")
    if screenshot is not None:
        flags.append(f"--screenshot={screenshot}")
    return flags


def run_chrome(chrome: str, url: str, width: int, height: int,
               tmp_profile: Path, timeout: int, dump: bool = True,
               screenshot: Path | None = None) -> tuple[str, str, int]:
    """Run headless Chrome. Returns (stdout, stderr, returncode)."""
    attempts = [
        chrome_flags(tmp_profile, dump, screenshot, width, height),
        # Older Chrome builds do not know --headless=new.
        [f for f in chrome_flags(tmp_profile, dump, screenshot, width, height)
         if f != "--headless=new"],
    ]
    last = ("", "chrome not executed", 1)
    for flags in attempts:
        try:
            proc = subprocess.run(
                [chrome, *flags, url],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return ("", "timed out", 124)
        except OSError as exc:
            return ("", str(exc), 127)
        if proc.returncode == 0 and (proc.stdout.strip() or not dump):
            return (proc.stdout, proc.stderr, proc.returncode)
        last = (proc.stdout, proc.stderr, proc.returncode)
    return last


# ── probe injection ───────────────────────────────────────────────────────


def inject_probe(html: str, probe: str) -> str:
    # A literal closing tag inside the probe would end the injected element
    # early (and would confuse the injection points below).
    probe = probe.replace("</script>", "<\\/script>").replace("</body>", "<\\/body>")
    tag = f"<script>{probe}</script>"

    # Body first: the head injection would otherwise be found by the body
    # search if the probe itself mentioned a closing body tag.
    m = re.search(r"</body>", html, re.I)
    if m:
        html = html[: m.start()] + tag + html[m.start():]
    else:
        m = re.search(r"</html>", html, re.I)
        if m:
            html = html[: m.start()] + tag + html[m.start():]
        else:
            html = html + tag

    m = re.search(r"<head[^>]*>", html, re.I)
    if m:
        html = html[: m.end()] + tag + html[m.end():]
    else:
        m = re.search(r"<html[^>]*>", html, re.I)
        if m:
            html = html[: m.end()] + tag + html[m.end():]
        else:
            html = tag + html
    return html


def extract_result(dom: str, rid: str = "__ds_probe__") -> dict | None:
    m = re.search(
        r'<script\s[^>]*?\sid="' + re.escape(rid) + r'"[^>]*>(.*?)</script>', dom, re.S
    )
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except (ValueError, TypeError):
        return None


def build_wrapper(width: int, height: int, artifact: str = "artifact.html") -> str:
    """A page that frames the artifact at an exact pixel size.

    Headless Chrome clamps the *window* to ~500px wide on desktop, so a
    narrow viewport cannot be requested with --window-size alone. An iframe
    gets the exact layout width, and the probe result is copied out of the
    frame into this page.
    """
    return f"""<!doctype html>
<html><head><meta charset="utf-8">
<style>
  html, body {{ margin: 0; padding: 0; background: #fff; }}
  /* Left-aligned: Chrome clamps the window to ~500px but the screenshot
     canvas stays at the requested width, so the artifact must start at x=0. */
  #ds-frame {{ display: block; border: 0; width: {width}px; height: {height}px; margin: 0; }}
</style>
<script>
(function () {{
  var best = null;
  function write(data) {{
    var s = JSON.stringify(data).replace(/</g, "\\\\u003c");
    var el = document.getElementById("__ds_result__");
    if (!el) {{
      el = document.createElement("script");
      el.type = "application/json";
      el.id = "__ds_result__";
      (document.body || document.documentElement).appendChild(el);
    }}
    el.textContent = s;
  }}
  function grab() {{
    var f = document.getElementById("ds-frame");
    if (!f) return;
    try {{
      var d = f.contentDocument;
      if (!d) return;
      var el = d.getElementById("__ds_probe__");
      if (!el || !el.textContent) return;
      var data = JSON.parse(el.textContent);
      if (!best || (data.late && !best.late)) {{ best = data; write(best); }}
    }} catch (e) {{ /* frame not ready */ }}
  }}
  window.addEventListener("load", function () {{
    setTimeout(grab, 50);
    setTimeout(grab, 500);
  }});
  setTimeout(grab, 2500);
  setTimeout(grab, 4500);
}})();
</script>
</head><body>
<iframe id="ds-frame" src="{artifact}" scrolling="no" title="artifact"></iframe>
</body></html>
"""


# ── probe result → findings ──────────────────────────────────────────────


def findings_from(data: dict, viewport: str) -> list[VFinding]:
    out: list[VFinding] = []

    if not data.get("ok"):
        out.append(VFinding(
            "P0", "probe-failed",
            f"The render probe did not complete at {viewport}.",
            "Report this — the artifact may throw during load. Open it in a browser and read the console.",
            detail=str(data.get("error", ""))[:160],
            viewports=[viewport],
        ))
        return out

    for err in data.get("errors") or []:
        out.append(VFinding(
            "P0", "runtime-error",
            f"JavaScript error at {viewport}: {err.get('message', 'unknown')}",
            "Fix the script error — the artifact ships broken behaviour even if the markup looks right.",
            detail=err.get("source", ""),
            viewports=[viewport],
        ))

    doc = data.get("doc") or {}
    if data.get("docOverflow"):
        out.append(VFinding(
            "P0", "overflow-x",
            f"The page scrolls horizontally at {viewport} "
            f"(content {doc.get('scrollWidth')}px in a {doc.get('clientWidth')}px viewport).",
            "Find the element named below and constrain it: `minmax(0, 1fr)` on grid tracks, "
            "`min-width: 0` on grid/flex children, and `overflow-wrap: anywhere` on long strings.",
            detail="",
            viewports=[viewport],
        ))

    for item in data.get("overflow") or []:
        out.append(VFinding(
            "P0", "overflow-element",
            f"`{item['sel']}` extends {item['right'] - (data.get('viewport', {}).get('w') or 0)}px "
            f"past the {viewport} viewport.",
            "Constrain the element — the page scrolls sideways and the layout breaks on mobile.",
            selector=item["sel"],
            detail=item.get("text", "")[:80],
            viewports=[viewport],
        ))
    for item in data.get("clipped") or []:
        where = f" (culprit: `{item['culprit']}`)" if item.get("culprit") else ""
        out.append(VFinding(
            "P0", "text-clipped",
            f"`{item['sel']}` cuts its content off at {viewport} "
            f"({item['scrollWidth']}px of content in a {item['clientWidth']}px box){where}.",
            "Let the box grow, scroll it deliberately, or remove the clipping — the text is invisible today.",
            selector=item["sel"],
            detail=(item.get("culpritText") or item.get("text", ""))[:80],
            viewports=[viewport],
        ))

    for item in data.get("contrast") or []:
        out.append(VFinding(
            "P0", "contrast-text",
            f"`{item['sel']}` renders at {item['ratio']}:1 — needs {item['required']}:1 "
            f"({item['size']}px, {item['color']} on {item['background']}).",
            "Raise the contrast to WCAG 2.2 AA (4.5:1 text, 3:1 large text) — adjust the token, "
            "not the individual element.",
            selector=item["sel"],
            detail=item.get("text", "")[:80],
            viewports=[viewport],
        ))

    for item in data.get("minContent") or []:
        if item.get("overflow"):
            out.append(VFinding(
                "P0", "min-content-overflow",
                f"`{item['sel']}` needs {item['minContent']}px but only {item['available']}px is "
                "available — it overflows, and a wider font fallback will make it worse.",
                "Give it a scroll container, let it wrap, or reduce the content — the layout must "
                "survive a different font.",
                selector=item["sel"],
                viewports=[viewport],
            ))
        else:
            out.append(VFinding(
                "P1", "tight-fit",
                f"`{item['sel']}` fits with only {item['available'] - item['minContent']}px to "
                "spare — a slightly wider font fallback will push it over.",
                "Leave a little slack, or give the element a scroll container so the page never "
                "scrolls sideways.",
                selector=item["sel"],
                viewports=[viewport],
            ))

    for item in data.get("tapTargets") or []:
        out.append(VFinding(
            "P1", "tap-target-small",
            f"`{item['sel']}` is {item['width']}×{item['height']}px at {viewport} — "
            "WCAG 2.2 AA wants 24×24px.",
            "Give the control a 24×24px hit area (padding or min-width/min-height).",
            selector=item["sel"],
            detail=item.get("text", "")[:80],
            viewports=[viewport],
        ))

    for item in data.get("images") or []:
        out.append(VFinding(
            "P1", "img-missing-dimensions",
            f"`{item['sel']}` has no width/height attribute — the image shifts the layout on load.",
            "Set intrinsic `width` and `height` attributes on every <img>.",
            selector=item["sel"],
            detail=item.get("src", "")[:80],
            viewports=[viewport],
        ))

    focus = data.get("focus") or {}
    if not focus.get("rules"):
        out.append(VFinding(
            "P1", "focus-style-missing",
            "No `:focus` / `:focus-visible` rule ships with the artifact — keyboard users "
            "cannot see where they are.",
            "Add a visible focus ring (`:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px }`).",
            viewports=[viewport],
        ))
    elif not focus.get("hasIndicator"):
        out.append(VFinding(
            "P1", "focus-indicator-removed",
            "The focus rules remove the indicator without replacing it.",
            "Give `:focus-visible` an outline or box-shadow instead of `outline: none`.",
            detail=", ".join(focus.get("selectors", [])[:3]),
            viewports=[viewport],
        ))

    meta = data.get("viewportMeta")
    if meta is None:
        out.append(VFinding(
            "P1", "viewport-meta-missing",
            "No `<meta name=\"viewport\">` — mobile browsers will not reflow the page.",
            "Add `<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">`.",
            viewports=[viewport],
        ))
    elif re.search(r"user-scalable\s*=\s*no|maximum-scale\s*=\s*1\b", meta, re.I):
        out.append(VFinding(
            "P1", "zoom-blocked",
            "The viewport meta blocks zoom.",
            "Drop `user-scalable=no` and `maximum-scale=1` — zoom is an accessibility requirement.",
            detail=meta[:80],
            viewports=[viewport],
        ))

    for item in data.get("truncated") or []:
        out.append(VFinding(
            "P2", "text-truncated",
            f"`{item['sel']}` truncates with an ellipsis at {viewport} — confirm the full value "
            "is reachable elsewhere.",
            "Expose the full value on hover/focus, or in a tooltip that is not hover-only.",
            selector=item["sel"],
            detail=item.get("text", "")[:80],
            viewports=[viewport],
        ))

    return out


def merge(findings: list[VFinding]) -> list[VFinding]:
    """Fold identical findings across viewports into one entry."""
    merged: dict[tuple, VFinding] = {}
    for f in findings:
        k = f.key()
        if k in merged:
            for v in f.viewports:
                if v not in merged[k].viewports:
                    merged[k].viewports.append(v)
        else:
            merged[k] = f
    out = list(merged.values())
    out.sort(key=lambda f: (SEVERITY_ORDER[f.severity], f.id, f.selector))
    return out


# ── per-file verification ─────────────────────────────────────────────────


def has_stylesheet(raw: str) -> bool:
    return bool(
        re.search(r"<style[\s>]", raw, re.I)
        or re.search(r"rel\s*=\s*[\"']?stylesheet", raw, re.I)
    )


def verify_file(path: Path, chrome: str, viewports: list[tuple[int, int]],
                timeout: int, shot_dir: Path | None) -> VFile:
    vf = VFile(path=str(path))
    raw = path.read_text(encoding="utf-8")
    if not has_stylesheet(raw):
        vf.skipped = "paste-ready fragment — no stylesheet of its own"
        return vf
    probe = PROBE.read_text(encoding="utf-8")
    injected = inject_probe(raw, probe)

    all_findings: list[VFinding] = []
    with tempfile.TemporaryDirectory(prefix="design-studio-verify.") as tmp:
        tmpdir = Path(tmp)
        tmp_html = tmpdir / "artifact.html"
        tmp_html.write_text(injected, encoding="utf-8")
        artifact_url = tmp_html.resolve().as_uri()
        profile = tmpdir / "profile"

        for width, height in viewports:
            wrapper = tmpdir / f"wrapper-{width}x{height}.html"
            wrapper.write_text(build_wrapper(width, height), encoding="utf-8")
            wrapper_url = wrapper.resolve().as_uri()

            stdout, stderr, code = run_chrome(
                chrome, wrapper_url, width, height, profile, timeout, dump=True
            )
            data = extract_result(stdout, "__ds_result__")
            if data is None:
                # Fall back to rendering the artifact directly.
                stdout, stderr, code = run_chrome(
                    chrome, artifact_url, width, height, profile, timeout, dump=True
                )
                data = extract_result(stdout, "__ds_probe__")
            if data is None:
                vf.error = (
                    f"no render result at {width}x{height} "
                    f"(chrome exit {code}): {clip(stderr or 'no output')}"
                )
                break

            label = f"{width}x{height}"
            vp_info = {
                "viewport": label,
                "measured": data.get("viewport", {}),
                "doc": data.get("doc", {}),
                "counts": data.get("counts", {}),
                "contrastSkipped": data.get("contrastSkipped", 0),
                "late": bool(data.get("late")),
                "framed": data.get("viewport", {}).get("w") == width,
            }
            vf.viewports.append(vp_info)
            all_findings.extend(findings_from(data, label))

            if shot_dir is not None:
                shot_dir.mkdir(parents=True, exist_ok=True)
                shot = shot_dir / f"{path.stem}-{width}x{height}.png"
                if shot.exists():
                    shot.unlink()
                run_chrome(
                    chrome, wrapper_url, width, height, profile, timeout,
                    dump=False, screenshot=shot,
                )
                crop_screenshot(shot, width, height)

    vf.findings = merge(all_findings)
    return vf


def png_size(path: Path) -> tuple[int, int] | None:
    """Read width/height from a PNG header (bytes 16-24 of the IHDR chunk)."""
    try:
        head = path.read_bytes()[:24]
    except OSError:
        return None
    if len(head) < 24 or head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return (
        int.from_bytes(head[16:20], "big"),
        int.from_bytes(head[20:24], "big"),
    )


def crop_screenshot(path: Path, width: int, height: int) -> None:
    """Trim the window padding around the framed artifact, when we can.

    The frame sits at the top-left of the window, so the crop is anchored
    there. macOS `sips` and ImageMagick can do it; without them the padded
    PNG is left as-is.
    """
    size = png_size(path)
    if not size or (size[0] <= width and size[1] <= height):
        return
    for cmd in (
        ["sips", "-c", str(height), str(width), "--cropOffset", "0", "0", str(path)],
        ["magick", str(path), "-crop", f"{width}x{height}+0+0", "+repage", str(path)],
        ["convert", str(path), "-crop", f"{width}x{height}+0+0", "+repage", str(path)],
    ):
        if shutil.which(cmd[0]):
            try:
                subprocess.run(cmd, capture_output=True, timeout=30)
                return
            except (OSError, subprocess.TimeoutExpired):
                continue


def clip(s: str, n: int = 160) -> str:
    s = " ".join((s or "").split())
    return s[: n - 1] + "…" if len(s) > n else s


# ── CLI ───────────────────────────────────────────────────────────────────


def parse_viewports(spec: str) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    for part in spec.split(","):
        part = part.strip().lower()
        if not part:
            continue
        m = re.match(r"^(\d+)\s*[x×]\s*(\d+)$", part)
        if not m:
            raise ValueError(f"bad viewport: {part!r} (expected WxH)")
        out.append((int(m.group(1)), int(m.group(2))))
    return out or list(DEFAULT_VIEWPORTS)


def main(argv: list[str]) -> int:
    as_json = "--json" in argv
    want_shot = "--screenshot" in argv
    no_browser = "--no-browser" in argv
    require_browser = "--require-browser" in argv
    timeout = 45
    shot_dir: Path | None = None
    viewports = list(DEFAULT_VIEWPORTS)
    fail_on = "p0"

    i = 1
    files: list[str] = []
    while i < len(argv):
        a = argv[i]
        if a == "--screenshot":
            i += 1
            shot_dir = Path(argv[i]) if i < len(argv) else Path(".")
        elif a == "--viewports":
            i += 1
            viewports = parse_viewports(argv[i] if i < len(argv) else "")
        elif a == "--timeout":
            i += 1
            timeout = int(argv[i]) if i < len(argv) else 45
        elif a == "--fail-on":
            i += 1
            fail_on = (argv[i] if i < len(argv) else "p0").lower()
        elif not a.startswith("-"):
            files.append(a)
        i += 1

    if not files:
        print(__doc__.strip())
        return 2

    if no_browser:
        if as_json:
            print(json.dumps({"files": [], "total_p0": 0, "skipped": "no-browser"}))
        else:
            print("verify · skipped (--no-browser)")
        return 0

    chrome = find_chrome()
    if not chrome:
        msg = (
            "no Chrome or Chromium found — render verification skipped.\n"
            "  Install Chrome/Chromium, or run with --no-browser to silence this."
        )
        if require_browser:
            print(msg, file=sys.stderr)
            return 2
        if as_json:
            print(json.dumps({"files": [], "total_p0": 0, "skipped": "no-browser"}))
        else:
            print(msg)
        return 0

    report: list[dict] = []
    total = {"P0": 0, "P1": 0, "P2": 0}
    failures = 0

    for name in files:
        path = Path(name)
        if not path.is_file():
            if as_json:
                report.append({"path": name, "error": "file not found"})
            else:
                print(f"verify · {name}\n  skipped — file not found\n")
            continue

        vf = verify_file(path, chrome, viewports, timeout, shot_dir)
        counts = {s: sum(1 for f in vf.findings if f.severity == s) for s in ("P0", "P1", "P2")}
        for s in counts:
            total[s] += counts[s]

        threshold = SEVERITY_ORDER.get(fail_on, 0) if fail_on != "none" else 99
        blocking = [f for f in vf.findings if SEVERITY_ORDER[f.severity] <= threshold]
        if blocking:
            failures += 1

        if as_json:
            report.append({
                "path": vf.path,
                "error": vf.error,
                "skipped": vf.skipped,
                "counts": counts,
                "viewports": vf.viewports,
                "findings": [
                    {
                        "severity": f.severity,
                        "id": f.id,
                        "message": f.message,
                        "fix": f.fix,
                        "selector": f.selector,
                        "detail": f.detail,
                        "viewports": f.viewports,
                    }
                    for f in vf.findings
                ],
            })
            continue

        print(f"verify · {vf.path}")
        if vf.skipped:
            print(f"  skipped — {vf.skipped}")
        if vf.error:
            print(f"  ERROR — {vf.error}")
        for vp in vf.viewports:
            m = vp.get("measured", {})
            d = vp.get("doc", {})
            width = m.get("w") or "?"
            note = "" if vp.get("framed", True) else "  (window clamp — not the requested width)"
            print(
                f"  {vp['viewport']:>9} — layout {width}px · "
                f"content {d.get('scrollWidth')}px · "
                f"{vp.get('counts', {}).get('elements', 0)} elements{note}"
            )
        for f in vf.findings:
            where = f" · {', '.join(f.viewports)}" if f.viewports else ""
            print(f"  [{f.severity}] {f.id}{where} — {f.message}")
            print(f"        fix: {f.fix}")
            if f.selector:
                print(f"        near: `{f.selector}`")
            if f.detail:
                print(f"        text: {f.detail}")
        if not vf.findings:
            print("  clean — no findings.")
        verdict = "FAIL" if blocking else "pass"
        print(f"  {counts['P0']} P0 · {counts['P1']} P1 · {counts['P2']} P2 — {verdict}\n")

    if as_json:
        print(json.dumps({
            "files": report,
            "total_p0": total["P0"],
            "total_p1": total["P1"],
            "total_p2": total["P2"],
        }, indent=2))

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

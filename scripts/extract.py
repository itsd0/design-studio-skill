#!/usr/bin/env python3
"""
Design Studio — design system extractor.

Turns a live page, a local HTML file, or a reference screenshot into a
DESIGN.md brand contract plus a tokens.css twin. This is the instrument
the workflow was missing: step 2 of SKILL.md used to ask the agent to
"sample the core tokens" by eye.

Usage:
    python3 scripts/extract.py https://example.com --out ./brand
    python3 scripts/extract.py page.html --out ./brand
    python3 scripts/extract.py screenshot.png --out ./brand
    python3 scripts/extract.py https://example.com --json

Outputs DESIGN.md and tokens.css in --out (default: the working
directory). Nothing is written outside --out.
"""

from __future__ import annotations

import json
import math
import re
import sys
import tempfile
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import verify  # noqa: E402
from pngread import PngError, read_png  # noqa: E402

DESIGN_PROBE = Path(__file__).resolve().parent / "probe-design.js"

# ── colour maths ──────────────────────────────────────────────────────────


def hex_to_rgb(value: str) -> tuple[int, int, int] | None:
    v = value.strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if len(v) == 6:
        try:
            return (int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16))
        except ValueError:
            return None
    return None


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(c))) for c in rgb)


def _srgb_to_linear(c: float) -> float:
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c: float) -> int:
    c = max(0.0, min(1.0, c))
    v = c * 12.92 if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
    return round(v * 255)


def luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = (_srgb_to_linear(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def saturation(rgb: tuple[int, int, int]) -> float:
    r, g, b = (v / 255 for v in rgb)
    mx, mn = max(r, g, b), min(r, g, b)
    if mx == mn:
        return 0.0
    return (mx - mn) / mx


def lightness(rgb: tuple[int, int, int]) -> float:
    return (max(rgb) + min(rgb)) / 2 / 255


def oklch_to_rgb(L: float, C: float, H: float) -> tuple[int, int, int]:
    h = math.radians(H)
    a, b = C * math.cos(h), C * math.sin(h)
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return (_linear_to_srgb(r), _linear_to_srgb(g), _linear_to_srgb(bb))


def parse_css_color(value: str) -> tuple[int, int, int] | None:
    """Parse the colour serialisations a browser hands back."""
    if not value:
        return None
    v = value.strip()
    if v == "transparent":
        return None
    if v.startswith("#"):
        return hex_to_rgb(v)
    m = re.fullmatch(r"rgba?\(([^)]+)\)", v, re.I)
    if m:
        parts = [p for p in re.split(r"[\s,/]+", m.group(1)) if p]
        try:
            nums = [float(p) for p in parts[:3]]
        except ValueError:
            return None
        if len(nums) < 3:
            return None
        return (round(nums[0]), round(nums[1]), round(nums[2]))
    m = re.fullmatch(r"color\(srgb\s+([^)]+)\)", v, re.I)
    if m:
        parts = [p for p in re.split(r"[\s/]+", m.group(1)) if p]
        try:
            nums = [float(p) for p in parts[:3]]
        except ValueError:
            return None
        if any(p.endswith("%") for p in parts[:3]):
            nums = [float(p.rstrip("%")) * 2.55 for p in parts[:3]]
        else:
            nums = [n * 255 for n in nums]
        return (round(nums[0]), round(nums[1]), round(nums[2]))
    m = re.fullmatch(r"oklch\(\s*([\d.]+%?)\s+([\d.]+)\s+([\d.]+)(?:deg)?\s*\)", v, re.I)
    if m:
        raw_l = m.group(1)
        try:
            L = float(raw_l.rstrip("%")) / (100 if raw_l.endswith("%") else 1)
        except ValueError:
            return None
        return oklch_to_rgb(L, float(m.group(2)), float(m.group(3)))
    return None


# ── token inference ───────────────────────────────────────────────────────


def to_rgb(value: str) -> tuple[int, int, int] | None:
    """Any supported colour notation → sRGB 0-255."""
    return parse_css_color(value)


def pick_backgrounds(colors: list[dict], page: dict) -> tuple[str, str]:
    """The page background, then the next distinct surface above it."""
    bg = (parse_css_color(page.get("bodyBg") or "")
          or parse_css_color(page.get("htmlBg") or ""))
    if not bg:
        ranked = []
        for c in colors:
            rgb = parse_css_color(c["value"])
            if rgb and not (abs(rgb[0] - rgb[1]) < 6 and abs(rgb[1] - rgb[2]) < 6):
                ranked.append((c["count"], rgb))
        ranked.sort(key=lambda r: -r[0])
        bg = ranked[0][1] if ranked else (255, 255, 255)

    # The surface is the most common background that is clearly *not* the page
    # background — a card or panel colour.
    surface = bg
    candidates = []
    for c in colors:
        rgb = parse_css_color(c["value"])
        if not rgb or rgb == bg:
            continue
        if contrast(rgb, bg) < 0.03:
            continue
        candidates.append((c["count"], rgb))
    if candidates:
        candidates.sort(key=lambda c: -c[0])
        surface = candidates[0][1]
    return (rgb_to_hex(bg), rgb_to_hex(surface))


def pick_text(colors: list[dict], page: dict, bg: str) -> tuple[str, str]:
    """Body foreground, then a muted derived from it against the background."""
    fg = parse_css_color(page.get("bodyColor") or "")
    if not fg:
        ranked = []
        for c in colors:
            rgb = parse_css_color(c["value"])
            if rgb:
                ranked.append((c["count"], rgb))
        ranked.sort(key=lambda r: -r[0])
        fg = ranked[0][1] if ranked else (26, 26, 26)
    bg_rgb = hex_to_rgb(bg) or (255, 255, 255)
    # Muted is the foreground pulled back toward the background.
    muted = tuple(int(f * 0.62 + b * 0.38) for f, b in zip(fg, bg_rgb))
    return (rgb_to_hex(fg), rgb_to_hex(muted))


def pick_accent(link_colors: list[dict], button_fills: list[dict],
                heading_colors: list[dict], bg: str) -> tuple[str, str]:
    """The one chromatic colour the page uses to signal, plus its ink.

    Links win over button fills (a link colour is a deliberate brand
    choice), and near-black or near-white colours never qualify as an
    accent — they read as ink, not as a signal.
    """
    bg_rgb = hex_to_rgb(bg) or (255, 255, 255)

    def viable(entries, weight):
        out = []
        for c in entries:
            rgb = parse_css_color(c["value"])
            if not rgb:
                continue
            sat = saturation(rgb)
            light = lightness(rgb)
            if sat < 0.20 or light < 0.18 or light > 0.88:
                continue
            if contrast(rgb, bg_rgb) < 1.5:
                continue
            out.append((c["count"] * weight * (0.5 + sat), rgb))
        return out

    candidates = viable(link_colors, 3.0) + viable(button_fills, 2.0) \
        + viable(heading_colors, 1.2)
    if not candidates:
        return ("#3b82f6", "#ffffff")
    candidates.sort(key=lambda c: -c[0])
    accent = candidates[0][1]
    ink = (255, 255, 255) if luminance(accent) < 0.4 else (17, 17, 17)
    if contrast(ink, accent) < 4.5:
        ink = (255, 255, 255) if luminance(accent) < 0.4 else (0, 0, 0)
    return (rgb_to_hex(accent), rgb_to_hex(ink))


def pick_border(colors: list[dict], fg: str, bg: str) -> str:
    for c in colors:
        rgb = parse_css_color(c["value"])
        if rgb and saturation(rgb) < 0.25:
            return rgb_to_hex(rgb)
    fg_rgb = hex_to_rgb(fg) or (26, 26, 26)
    bg_rgb = hex_to_rgb(bg) or (255, 255, 255)
    return rgb_to_hex(tuple(int(f * 0.12 + b * 0.88) for f, b in zip(fg_rgb, bg_rgb)))


def infer_typography(typography: list[dict]) -> dict:
    """Group the observed type styles into display / body / mono + a scale."""
    display = body = mono = None
    sizes: set[int] = set()
    families: Counter = Counter()

    for entry in typography:
        parts = entry["value"].split("|")
        if len(parts) < 7:
            continue
        tag, family, size, weight, lh, ls, transform = parts[:7]
        try:
            px = float(size.replace("px", ""))
        except ValueError:
            continue
        sizes.add(int(round(px)))
        families[family] += entry["count"]
        if tag in ("h1", "h2", "h3") and display is None:
            display = {"family": family, "size": px, "weight": weight}
        if tag in ("p", "li", "td") and body is None:
            body = {"family": family, "size": px, "weight": weight}
        if tag in ("code", "pre") and mono is None:
            mono = {"family": family, "size": px, "weight": weight}

    common = families.most_common(1)[0][0] if families else "system-ui, sans-serif"
    display_family = display["family"] if display else common
    body_family = body["family"] if body else common
    mono_family = mono["family"] if mono else "ui-monospace, monospace"

    scale = sorted(sizes)[:12]
    if not scale:
        scale = [12, 14, 16, 20, 24, 32]
    return {
        "display": display_family,
        "body": body_family,
        "mono": mono_family,
        "scale": scale,
        "weight_display": display["weight"] if display else "600",
        "weight_body": body["weight"] if body else "400",
    }


def infer_scale(values: list[dict], base: int = 4) -> list[int]:
    """Round a histogram of spacing values onto a 4px scale."""
    counts = Counter()
    for v in values:
        try:
            px = int(v["value"])
        except (ValueError, TypeError):
            continue
        if px <= 0:
            continue
        step = base
        while px % step and step < px:
            step += 1
        counts[px] += v["count"]
    picked: list[int] = []
    for px, _ in counts.most_common():
        if all(abs(px - p) > max(2, base * 0.6) for p in picked):
            picked.append(px)
    return sorted(picked)[:8] or [8, 16, 24, 32]


# ── extraction ────────────────────────────────────────────────────────────


def fetch_html(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    return raw.decode("utf-8", errors="replace")


def absolutise(html: str, base: str) -> str:
    """Make relative asset URLs absolute so a fetched copy still renders."""
    from urllib.parse import urljoin

    def fix(match: re.Match) -> str:
        attr, url = match.group(1), match.group(2)
        if url.startswith(("http://", "https://", "data:", "#", "//")):
            return match.group(0)
        return f'{attr}="{urljoin(base, url)}"'

    return re.sub(r'\b(src|href|poster)="([^"]+)"', fix, html)


def render_probe(html: str, chrome: str, width: int = 1440, height: int = 900,
                 timeout: int = 45) -> dict | None:
    probe = DESIGN_PROBE.read_text(encoding="utf-8")
    injected = verify.inject_probe(html, probe)
    with tempfile.TemporaryDirectory(prefix="design-studio-extract.") as tmp:
        tmpdir = Path(tmp)
        page = tmpdir / "page.html"
        page.write_text(injected, encoding="utf-8")
        stdout, stderr, code = verify.run_chrome(
            chrome, page.resolve().as_uri(), width, height, tmpdir / "profile", timeout,
            dump=True,
        )
        if not stdout:
            return None
        return verify.extract_result(stdout, "__ds_design__")


def extract_from_png(path: Path, name: str) -> dict:
    width, height, pixels = read_png(path)
    counts: Counter = Counter()
    for r, g, b in pixels:
        counts[(r >> 4, g >> 4, b >> 4)] += 1
    buckets = [
        (count, ((k[0] << 4) | 8, (k[1] << 4) | 8, (k[2] << 4) | 8))
        for k, count in counts.items()
    ]
    buckets.sort(key=lambda c: -c[0])
    total = len(pixels)

    bg = buckets[0][1] if buckets else (255, 255, 255)
    # The most common *non-background* cluster is the surface.
    surface = next((c[1] for c in buckets[1:] if contrast(c[1], bg) > 0.08), bg)
    accent = next(
        (c[1] for c in buckets if saturation(c[1]) > 0.28 and contrast(c[1], bg) > 1.8),
        (59, 130, 246),
    )
    # Foreground: the darkest cluster if the page is light, the lightest if dark.
    dark = bg is not None and lightness(bg) > 0.5
    fg = next(
        (c[1] for c in buckets if (lightness(c[1]) < 0.35 if dark else lightness(c[1]) > 0.7)),
        (26, 25, 22) if dark else (17, 17, 17),
    )
    ink = (255, 255, 255) if luminance(accent) < 0.4 else (17, 17, 17)
    if contrast(ink, accent) < 4.5:
        ink = (255, 255, 255) if luminance(accent) < 0.4 else (0, 0, 0)

    return {
        "source": str(path),
        "kind": "screenshot",
        "width": width,
        "height": height,
        "pixels": total,
        "tokens": {
            "--bg": rgb_to_hex(bg),
            "--surface": rgb_to_hex(surface),
            "--fg": rgb_to_hex(fg),
            "--muted": rgb_to_hex(tuple(int(c * 0.55 + f * 0.45) for c, f in zip(fg, bg))),
            "--border": rgb_to_hex(tuple(int(c * 0.12 + f * 0.88) for c, f in zip(fg, bg))),
            "--accent": rgb_to_hex(accent),
            "--accent-on": rgb_to_hex(ink),
        },
        "note": (
            "Palette extracted from a screenshot. Typography, spacing and component "
            "styling cannot be measured from an image — fill them in before binding "
            "them to an artifact."
        ),
    }


def extract_from_page(html: str, chrome: str, source: str) -> dict:
    data = render_probe(html, chrome)
    if not data:
        raise SystemExit("extract: the page could not be rendered (no Chrome?)")

    page = data.get("page", {})
    bg, surface = pick_backgrounds(data["colors"]["background"], page)
    fg, muted = pick_text(data["colors"]["text"], page, bg)
    accent, accent_on = pick_accent(
        data["colors"].get("link", []), data["colors"].get("buttonBg", []),
        data["colors"].get("heading", []), bg,
    )
    border = pick_border(data["colors"]["border"], fg, bg)
    typo = infer_typography(data["typography"])
    spacing = infer_scale(data["spacing"]["padding"] + data["spacing"]["gap"])
    radius = data["radii"][0]["value"] + "px" if data["radii"] else "8px"
    shadow = data["shadows"][0]["value"] if data["shadows"] else "none"
    maxw = data["layout"]["maxWidths"][0]["value"] + "px" if data["layout"]["maxWidths"] else "1200px"

    return {
        "source": source,
        "kind": "page",
        "title": data.get("title", ""),
        "tokens": {
            "--bg": bg,
            "--surface": surface,
            "--fg": fg,
            "--muted": muted,
            "--border": border,
            "--accent": accent,
            "--accent-on": accent_on,
        },
        "typography": typo,
        "spacing": spacing,
        "radius": radius,
        "shadow": shadow,
        "max_width": maxw,
        "media": sorted(set(data.get("media", {}).get("queries", [])))[:8],
        "structure": data.get("structure", {}),
        "palette": [
            {"value": c["value"], "count": c["count"]}
            for c in (data["colors"]["background"] + data["colors"]["fill"])[:14]
        ],
    }


# ── output ────────────────────────────────────────────────────────────────


def tokens_css(result: dict) -> str:
    t = result["tokens"]
    typo = result.get("typography", {})
    lines = [
        "/* Design Studio — extracted tokens.",
        f" * Source: {result['source']}",
        " * Bind these verbatim; derive tones with color-mix(). */",
        ":root {",
        f"  --bg: {t['--bg']};",
        f"  --surface: {t['--surface']};",
        f"  --surface-2: {t['--surface']};",
        f"  --fg: {t['--fg']};",
        f"  --muted: {t['--muted']};",
        f"  --border: {t['--border']};",
        f"  --accent: {t['--accent']};",
        f"  --accent-on: {t['--accent-on']};",
    ]
    if typo:
        lines += [
            f"  --font-display: {typo['display']};",
            f"  --font-body: {typo['body']};",
            f"  --font-mono: {typo['mono']};",
        ]
    if result.get("radius"):
        lines.append(f"  --radius: {result['radius']};")
    if result.get("spacing"):
        for i, step in enumerate(result["spacing"][:6], start=1):
            lines.append(f"  --space-{i}: {step}px;")
    lines.append("}")
    return "\n".join(l for l in lines if l) + "\n"


def design_md(result: dict, name: str) -> str:
    t = result["tokens"]
    typo = result.get("typography", {})
    structure = result.get("structure", {})
    counts = structure.get("counts", {})

    out = [f"# {name}", ""]
    out.append(f"> Category: Extracted from {result['source']}")
    out.append(f"> Tokens below were measured from a rendered page — verify them against the "
               f"real product before shipping.")
    out.append("")
    out.append("## Visual Theme & Atmosphere")
    out.append(f"Derived from the source's own surfaces and type. {result.get('note', '')}".strip())
    out.append("")
    out.append("## Color Palette & Roles")
    out.append(f"- **Background:** `{t['--bg']}`")
    out.append(f"- **Surface:** `{t['--surface']}` — cards, modals")
    out.append(f"- **Foreground:** `{t['--fg']}`")
    out.append(f"- **Muted:** `{t['--muted']}` — secondary text, captions")
    out.append(f"- **Border:** `{t['--border']}`")
    out.append(f"- **Accent:** `{t['--accent']}` — primary CTAs, links, one hero element per screen")
    out.append(f"- **Accent-on:** `{t['--accent-on']}` — text on an accent fill")
    out.append("Never invent a colour outside this palette — use the closest token.")
    out.append("")
    out.append("## Typography Rules")
    if typo:
        out.append(f"- **Display / headings:** `{typo['display']}`, weight {typo.get('weight_display', '600')}")
        out.append(f"- **Body:** `{typo['body']}`, weight {typo.get('weight_body', '400')}")
        out.append(f"- **Mono:** `{typo['mono']}`")
        out.append(f"- Scale (px): {' · '.join(str(s) for s in typo.get('scale', []))}")
    else:
        out.append("- **Display / headings:** [stack], weight 600")
        out.append("- **Body:** [stack], weight 400")
    out.append("")
    out.append("## Component Stylings")
    out.append(f"- **Radius:** {result.get('radius', '8px')} — buttons, cards, inputs")
    out.append(f"- **Elevation:** {result.get('shadow', 'none')}")
    if counts:
        out.append(f"- **Surface inventory:** {', '.join(f'{k}×{v}' for k, v in list(counts.items())[:10])}")
    out.append("")
    out.append("## Layout Principles")
    out.append(f"- **Max width:** {result.get('max_width', '1200px')}")
    if result.get("spacing"):
        out.append(f"- **Spacing scale (px):** {' · '.join(str(s) for s in result['spacing'])}")
    if result.get("media"):
        out.append(f"- **Breakpoints seen:** {'; '.join(result['media'])}")
    out.append("")
    out.append("## Depth & Elevation")
    out.append(f"Flat by default; one raised level — `{result.get('shadow', 'none')}`.")
    out.append("")
    out.append("## Do's and Don'ts")
    out.append("- ✅ Bind the token block verbatim.")
    out.append("- ✅ One accent element per screen.")
    out.append("- ❌ No new hex values outside this palette.")
    out.append("")
    out.append("## Responsive Behavior")
    out.append("- **Desktop ≥ 1024px:** 12-col grid")
    out.append("- **Tablet 640–1023px:** 8-col grid")
    out.append("- **Phone < 640px:** 4-col grid; tables scroll inside their own box")
    out.append("")
    out.append("## Agent Prompt Guide")
    out.append("- When in doubt, subtract.")
    out.append("- Accent budget: at most 2 visible uses per screen.")
    out.append("- Token discipline: use the closest existing token and surface a warning comment.")
    out.append("")
    return "\n".join(out)


def main(argv: list[str]) -> int:
    as_json = "--json" in argv
    out_dir = Path(".")
    name = None
    target = None
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--out":
            i += 1
            out_dir = Path(argv[i]) if i < len(argv) else Path(".")
        elif a == "--name":
            i += 1
            name = argv[i] if i < len(argv) else None
        elif not a.startswith("-"):
            target = a
        i += 1

    if not target:
        print(__doc__.strip())
        return 2

    if name is None:
        stem = re.sub(r"^https?://", "", target).strip("/").replace("/", "-")
        name = stem.split(".")[0][:1].upper() + stem.split(".")[0][1:] or "Extracted brand"

    chrome = verify.find_chrome()
    path = Path(target)

    if path.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") and path.is_file():
        try:
            result = extract_from_png(path, name)
        except PngError as exc:
            print(f"extract: cannot read image — {exc}", file=sys.stderr)
            return 1
    else:
        if not chrome:
            print("extract: no Chrome or Chromium found — cannot render the page.",
                  file=sys.stderr)
            return 2
        if re.match(r"^https?://", target):
            try:
                html = fetch_html(target)
            except Exception as exc:
                print(f"extract: could not fetch {target} — {exc}", file=sys.stderr)
                return 1
            html = absolutise(html, target)
        elif path.is_file():
            html = path.read_text(encoding="utf-8", errors="replace")
        else:
            print(f"extract: {target} is not a URL, an HTML file or an image", file=sys.stderr)
            return 2
        result = extract_from_page(html, chrome, target)

    if as_json:
        print(json.dumps(result, indent=2))
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "DESIGN.md").write_text(design_md(result, name), encoding="utf-8")
    (out_dir / "tokens.css").write_text(tokens_css(result), encoding="utf-8")
    print(f"extract · {result['source']}")
    print(f"  wrote {out_dir / 'DESIGN.md'}")
    print(f"  wrote {out_dir / 'tokens.css'}")
    if result.get("note"):
        print(f"  note: {result['note']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

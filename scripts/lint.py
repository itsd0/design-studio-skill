#!/usr/bin/env python3
"""
Design Studio anti-slop linter.

Greppy, deterministic, no dependencies. It does NOT parse HTML — a finding
always includes a snippet so you can verify it. Rules mirror
references/quality-gates.md ("the seven cardinal sins" + soft tells).

Usage:
    python3 scripts/lint.py artifact.html [more.html ...]

Exit status: 1 if any P0 finding (must fix before delivery), else 0.
P0/P1/P2 meaning: see references/quality-gates.md.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# ── pattern tables (keep in sync with references/quality-gates.md) ────────

PURPLE_HEXES = [
    # Tailwind violet / purple — the original AI-slop palette.
    "#a855f7", "#9333ea", "#7c3aed", "#6d28d9", "#581c87",
    "#8b5cf6", "#a78bfa", "#c4b5fd", "#ddd6fe", "#ede9fe",
    # Tailwind indigo.
    "#6366f1", "#4f46e5", "#4338ca", "#3730a3", "#312e81",
    "#818cf8", "#a5b4fc", "#c7d2fe", "#e0e7ff", "#eef2ff",
]

# Blue / cyan stops used in the "blue→cyan two-stop trust gradient" sin.
TRUST_GRADIENT_BLUE_HEXES = [
    "#3b82f6", "#2563eb", "#1d4ed8", "#1e40af", "#1e3a8a",
    "#60a5fa", "#93c5fd", "#bfdbfe",
    "#0ea5e9", "#0284c7", "#0369a1", "#38bdf8", "#7dd3fc",
]
TRUST_GRADIENT_CYAN_HEXES = [
    "#06b6d4", "#0891b2", "#0e7490", "#155e75", "#164e63",
    "#22d3ee", "#67e8f9", "#a5f3fc",
]

# The canonical "default LLM accent" — one solid use is already a tell.
AI_DEFAULT_INDIGO = [
    "#6366f1", "#4f46e5", "#4338ca", "#3730a3",
    "#8b5cf6", "#7c3aed", "#a855f7",
]

SLOP_EMOJI = [
    "✨", "🚀", "🎯", "⚡", "🔥", "💡", "📈", "🎨", "🛡️", "🌟",
    "💪", "🎉", "👋", "🙌", "✅", "⭐", "🏆",
]

INVENTED_METRIC_PATTERNS = [
    re.compile(r"\b10×\s+(faster|better|easier)\b", re.I),
    re.compile(r"\b100×\s+(faster|better)\b", re.I),
    re.compile(r"\b99\.\d+%\s+uptime\b", re.I),
    re.compile(r"\bzero[- ]downtime\b", re.I),
    re.compile(r"\b3×\s+more\s+(productive|efficient)\b", re.I),
]

FILLER_PATTERNS = [
    re.compile(r"\bfeature\s+(one|two|three|1|2|3)\b", re.I),
    re.compile(r"\blorem\s+ipsum\b", re.I),
    re.compile(r"\bdolor\s+sit\s+amet\b", re.I),
    re.compile(r"\bplaceholder\s+text\b", re.I),
    re.compile(r"\bsample\s+content\b", re.I),
]

# A heading rule that lands on Inter / Roboto / Arial / system-sans as the
# display face instead of the serif the seed binds.
DISPLAY_SANS_RE = re.compile(
    r"""(?:h1|h2|h3|\.h-?(?:hero|xl|lg|md))[^{}]*\{[^}]*font-family\s*:\s*["']?(?:Inter|Roboto|Arial|-apple-system|system-ui|SF\s+Pro)""",
    re.I,
)

GLOBAL_THEME_ATTRIBUTES = {"data-theme", "data-color-scheme", "data-mode"}
ROOT_FONT_PX = 16


@dataclass
class Finding:
    severity: str  # P0 | P1 | P2
    id: str
    message: str
    fix: str
    snippet: str = ""


# ── main entry ─────────────────────────────────────────────────────────────


def lint(raw_html: str) -> list[Finding]:
    out: list[Finding] = []
    if not raw_html:
        return out

    # Strip HTML comments before any pattern matching — pedagogical examples
    # inside comments ("paste a <section class="slide"> here") would fire.
    html = re.sub(r"<!--[\s\S]*?-->", "", raw_html)

    # ── P0-1: purple gradient backgrounds ─────────────────────────────
    for hexv in PURPLE_HEXES:
        m = re.search(r"linear-gradient\([^)]*" + re.escape(hexv) + r"[^)]*\)", html, re.I)
        if m:
            out.append(Finding(
                "P0", "purple-gradient",
                f"Found a violet/purple gradient using {hexv} — anti-slop list says no.",
                "Replace the gradient with a flat surface (var(--bg) or var(--surface)) or use the active accent at a single intensity, not in a gradient.",
                clip(m.group(0)),
            ))
            break
    if not any(f.id == "purple-gradient" for f in out):
        m = re.search(r"linear-gradient\([^)]*\b(purple|violet)\b[^)]*\)", html, re.I)
        if m:
            out.append(Finding(
                "P0", "purple-gradient",
                f'Found a "{m.group(1)}" keyword inside a gradient — anti-slop.',
                "Remove the gradient or swap to a single solid color from the active design tokens.",
                clip(m.group(0)),
            ))

    # ── P0-1c: blue→cyan "trust" two-stop gradient ────────────────────
    if not any(f.id == "purple-gradient" for f in out):
        tg = detect_blue_cyan_trust_gradient(html)
        if tg:
            out.append(Finding(
                "P0", "trust-gradient",
                'Found a blue→cyan two-stop "trust" gradient — anti-slop list says no.',
                "Replace the gradient with a flat surface (var(--bg) or var(--surface)) or use a single design-token color. Two-stop blue→cyan trust gradients are a SaaS hero cliché.",
                clip(tg),
            ))

    # ── P0-1b: solid AI-default indigo as accent ──────────────────────
    # Token blocks that legitimately declare `--accent: <indigo>` (a global
    # theme scope) are exempt; indigo laundered through any other token
    # name, a component selector, or the rendered body still fires.
    if not any(f.id == "purple-gradient" for f in out):
        scan = strip_token_blocks(html)
        for hexv in AI_DEFAULT_INDIGO:
            m = re.search(re.escape(hexv), scan, re.I)
            if m:
                out.append(Finding(
                    "P0", "ai-default-indigo",
                    f"Found a default LLM accent color ({hexv}) — this is the most-reported AI design tell.",
                    "Replace with var(--accent) from the active DESIGN.md. If the brief truly requires indigo, encode it as the design system's accent so it reads as intentional, not default.",
                    clip(m.group(0)),
                ))
                break

    # ── P0-2: emoji used as feature/UI icons ──────────────────────────
    for e in SLOP_EMOJI:
        if e in html:
            m = re.search(
                r'<(?:h[1-6]|button|li|span class="[^"]*icon[^"]*")[^>]*>[^<]*' + re.escape(e),
                html, re.I,
            )
            if m:
                out.append(Finding(
                    "P0", "emoji-icon",
                    f'Emoji "{e}" used as a UI icon — anti-slop list says SVG monoline only.',
                    "Replace with a small inline SVG icon (1.6–1.8px stroke, currentColor) or remove the icon entirely.",
                    clip(m.group(0)),
                ))
                break

    # ── P0-3: rounded card with left-border accent ────────────────────
    m = re.search(
        r"\.[a-z-]+\s*\{[^}]*border-left\s*:\s*\d+px\s+solid\s+[^;]+;[^}]*border-radius\s*:\s*[1-9]",
        html, re.I,
    )
    if m:
        out.append(Finding(
            "P0", "left-accent-card",
            "Rounded card with a coloured left border — the canonical AI-slop card pattern.",
            "Drop either the border-radius (set 0px) or the border-left. Cards in the seed templates use hairline borders all-round, no left accent.",
            clip(m.group(0)),
        ))

    # ── P0-4: sans-serif display face ─────────────────────────────────
    m = DISPLAY_SANS_RE.search(html)
    if m:
        out.append(Finding(
            "P0", "sans-display",
            "A heading rule uses Inter / Roboto / system-sans as the display face — not the serif the seed binds.",
            'Use `font-family: var(--font-display)` on h1/h2/h3 and let the active design system pick the serif. Override only if the active direction is "tech / utility" or "modern minimal".',
            clip(m.group(0)),
        ))

    # ── P0-5: invented metric phrasing ────────────────────────────────
    for rex in INVENTED_METRIC_PATTERNS:
        m = rex.search(html)
        if m:
            out.append(Finding(
                "P0", "invented-metric",
                f'Suspected invented metric: "{m.group(0)}". Anti-slop list says: no numbers without a real source.',
                "Either remove the claim or replace with a placeholder (— or a labelled stub) until the user supplies a real number.",
                clip(m.group(0)),
            ))
            break

    # ── P0-6: filler / lorem text ─────────────────────────────────────
    for rex in FILLER_PATTERNS:
        m = rex.search(html)
        if m:
            out.append(Finding(
                "P0", "filler-copy",
                f'Filler copy detected: "{m.group(0)}". Pages should ship with real, brief-derived copy.',
                "Replace with copy specific to the brief or delete the section entirely. An empty section is a design problem to solve with composition, not by inventing words.",
                clip(m.group(0)),
            ))
            break

    # ── P0-7: scrollIntoView (breaks iframe preview) ──────────────────
    if re.search(r"\.scrollIntoView\s*\(", html):
        out.append(Finding(
            "P0", "scroll-into-view",
            'Element.scrollIntoView() detected — yanks the host page when an iframe boundary is crossed.',
            'Use `scrollTo({ left, top, behavior: "smooth" })` on the actual scroller (see the deck seed for the proven pattern).',
        ))

    # ── P0-8: slides without a theme class ────────────────────────────
    # Deck-specific: triggered only if the artifact looks deck-shaped.
    slide_matches: list[str] = []
    if re.search(r"""class\s*=\s*["'][^"']*\bslide\b""", html):
        slide_matches = re.findall(
            r"""<section\s+class\s*=\s*["'][^"']*\bslide\b[^"']*["']""", html, re.I
        )
        themed = [
            s for s in slide_matches
            if re.search(r"\b(light|dark|hero\s+light|hero\s+dark)\b", s)
        ]
        if slide_matches and len(themed) < len(slide_matches):
            out.append(Finding(
                "P0", "slide-theme-missing",
                f"{len(slide_matches) - len(themed)} of {len(slide_matches)} slides lack a theme class (light / dark / hero light / hero dark).",
                'Every <section class="slide"> must include exactly one theme class. Audit your slide list and add light/dark/hero modifiers.',
            ))

    # ── P1-0: ALL-CAPS without letter-spacing ─────────────────────────
    token_scopes = extract_css_tokens(html)
    found_caps = False
    for block in re.finditer(r"<style[^>]*>([\s\S]*?)</style>", html, re.I):
        css = re.sub(r"/\*[\s\S]*?\*/", "", block.group(1))
        for m in re.finditer(r"([^{}]*)\{([^{}]*text-transform\s*:\s*uppercase[^{}]*)\}", css, re.I):
            selector = m.group(1).strip()
            body = m.group(2)
            if not has_adequate_uppercase_tracking(body, token_scopes):
                out.append(Finding(
                    "P1", "all-caps-no-tracking",
                    f"Selector `{selector[:60]}` sets text-transform: uppercase without sufficient letter-spacing (≥0.06em).",
                    "Add `letter-spacing: 0.08em` (typical) to the same rule. ALL CAPS without tracking looks cramped — the typography rules call this out as a top-tier amateur tell.",
                    clip(f"{selector} {{ {body.strip()} }}"),
                ))
                found_caps = True
                break
        if found_caps:
            break
    if not found_caps:
        for im in re.finditer(r"""(?:^|\s)style\s*=\s*(["'])([\s\S]*?)\1""", html):
            decl = im.group(2)
            if not re.search(r"text-transform\s*:\s*uppercase", decl, re.I):
                continue
            if not has_adequate_uppercase_tracking(decl, token_scopes):
                out.append(Finding(
                    "P1", "all-caps-no-tracking",
                    "Inline style sets text-transform: uppercase without sufficient letter-spacing (≥0.06em).",
                    "Add `letter-spacing: 0.08em` (typical) to the same inline style. ALL CAPS without tracking looks cramped.",
                    clip(decl.strip()),
                ))
                break

    # ── P1-1: external image CDNs ─────────────────────────────────────
    m = re.search(
        r"""<img[^>]+src=["']https?://(?:images\.unsplash\.com|placehold\.co|placekitten\.com|via\.placeholder\.com|picsum\.photos|loremflickr\.com)""",
        html, re.I,
    )
    if m:
        out.append(Finding(
            "P1", "external-image",
            "External placeholder image CDN detected — fragile, looks fake when it 404s.",
            "Use the .ph-img placeholder class shipped in the seed templates instead.",
            clip(m.group(0)),
        ))

    # ── P1-2: raw hex outside :root ───────────────────────────────────
    sm = re.search(r"<style[^>]*>([\s\S]*?)</style>", html, re.I)
    if sm:
        css = re.sub(r":root\s*\{[^}]*\}", "", sm.group(1))
        hexes = re.findall(r"#[0-9a-fA-F]{3,8}\b", css)
        if len(hexes) > 12:
            out.append(Finding(
                "P1", "raw-hex",
                f"{len(hexes)} raw hex values found outside :root — design tokens probably not honoured.",
                "Move every color into the :root token block (--bg / --surface / --fg / --muted / --border / --accent) and reference via var(). Use color-mix() for derived tones.",
                " ".join(hexes[:6]),
            ))

    # ── P1-3: too many accent uses inline in the rendered body ────────
    style_stripped = re.sub(r"<style[\s\S]*?</style>", "", html, flags=re.I)
    accent_uses = len(re.findall(r"var\(--accent\)", style_stripped))
    if accent_uses > 6:
        out.append(Finding(
            "P1", "accent-overuse",
            f"var(--accent) used {accent_uses} times inline in the body — likely overused per screen.",
            "Cap accent usage at 2 visible uses per screen (one eyebrow + one CTA, OR one accent card + one tab). Demote the rest to var(--fg) or var(--muted).",
        ))

    # ── P1-4: deck theme rhythm — no 3+ same-theme in a row ───────────
    if slide_matches:
        theme_seq = []
        for s in slide_matches:
            if re.search(r"hero\s+dark", s):
                theme_seq.append("HD")
            elif re.search(r"hero\s+light", s):
                theme_seq.append("HL")
            elif re.search(r"\bdark\b", s):
                theme_seq.append("D")
            elif re.search(r"\blight\b", s):
                theme_seq.append("L")
        for i in range(len(theme_seq) - 2):
            window = theme_seq[i:i + 3]
            if window in (["L", "L", "L"], ["HL", "HL", "HL"], ["D", "D", "D"], ["HD", "HD", "HD"]) or (
                all(t in ("L", "HL") for t in window) or all(t in ("D", "HD") for t in window)
            ):
                out.append(Finding(
                    "P1", "slide-rhythm",
                    f"Three same-theme slides in a row at position {i + 1}–{i + 3} — visual fatigue.",
                    "Swap the middle slide to the opposite theme (light → dark, or dark → light). For 8+ slides, mix in at least one hero light AND one hero dark.",
                ))
                break

    # ── P2-1: missing comment-mode anchor on <section> ────────────────
    sections = re.findall(r"<section\b[^>]*>", html, re.I)
    tagged = [
        s for s in sections
        if re.search(r"data-design-id\s*=", s) or re.search(r"data-screen-label\s*=", s)
    ]
    if sections and len(tagged) < len(sections):
        out.append(Finding(
            "P2", "missing-section-anchor",
            f"{len(sections) - len(tagged)} of {len(sections)} <section>s lack data-design-id (or data-screen-label).",
            'Add data-design-id="kebab-slug" (or data-screen-label="01 Cover" for slides) to every top-level <section> so an editor or agent can target it.',
        ))

    return out


# ── CSS helpers (uppercase-tracking check, token scopes) ──────────────────


def extract_css_tokens(html: str) -> list[dict]:
    scopes: list[dict] = []
    for block in re.finditer(r"<style[^>]*>([\s\S]*?)</style>", html, re.I):
        css = re.sub(r"/\*[\s\S]*?\*/", "", block.group(1))
        for m in re.finditer(r"([^{}]*)\{([^{}]*)\}", css):
            sel = m.group(1).strip()
            if not selector_list_is_global_theme_scope(sel):
                continue
            selectors = [s.strip() for s in sel.split(",") if s.strip()]
            is_default = any(is_bare_global_selector(s) for s in selectors)
            theme_keys = {s for s in selectors if not is_bare_global_selector(s)}
            tokens: dict[str, str] = {}
            for decl in (d.strip() for d in m.group(2).split(";")):
                if not decl:
                    continue
                dm = re.match(r"^(--[\w-]+)\s*:\s*(.+)$", decl)
                if dm:
                    tokens[dm.group(1)] = dm.group(2).strip()
            if not tokens:
                continue
            scopes.append({
                "selectors": selectors,
                "tokens": tokens,
                "is_default": is_default,
                "theme_keys": theme_keys,
            })
    return scopes


def build_resolved_themes(scopes: list[dict]) -> list[dict]:
    theme_keys = ["default"]
    for scope in scopes:
        for k in scope["theme_keys"]:
            if k not in theme_keys:
                theme_keys.append(k)
    themes: dict[str, dict] = {k: {} for k in theme_keys}
    for scope in scopes:
        if scope["is_default"]:
            for tmap in themes.values():
                tmap.update(scope["tokens"])
        else:
            for k in scope["theme_keys"]:
                if k in themes:
                    themes[k].update(scope["tokens"])
    return list(themes.values())


VAR_RE = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*))?\)")


def resolve_css_vars(body: str, tokens: dict) -> str:
    out = body
    for _ in range(4):
        def repl(m: re.Match) -> str:
            name, fallback = m.group(1), m.group(2)
            if name in tokens:
                return tokens[name]
            if fallback is not None:
                return fallback.strip()
            return m.group(0)
        nxt = VAR_RE.sub(repl, out)
        if nxt == out:
            break
        out = nxt
    return out


def has_adequate_uppercase_tracking(body: str, scopes: list[dict]) -> bool:
    for theme_map in build_resolved_themes(scopes):
        resolved = resolve_css_vars(body, theme_map)
        if not is_resolved_tracking_adequate(resolved):
            return False
    return True


def parse_declarations(body: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for raw in body.split(";"):
        idx = raw.find(":")
        if idx < 0:
            continue
        prop = raw[:idx].strip().lower()
        if not prop or prop.startswith("--"):
            continue
        value = raw[idx + 1:].strip()
        if not value:
            continue
        out.append((prop, value))
    return out


def find_last_decl(decls: list[tuple[str, str]], prop: str) -> tuple[str, str] | None:
    for decl in reversed(decls):
        if decl[0] == prop:
            return decl
    return None


def resolve_font_size_px(decls: list[tuple[str, str]]) -> float | None:
    fs = find_last_decl(decls, "font-size")
    if not fs:
        return None
    m = re.match(r"^(-?\d*\.?\d+)\s*(px|rem)\b", fs[1], re.I)
    if not m:
        return None
    v = float(m.group(1))
    return v * ROOT_FONT_PX if m.group(2).lower() == "rem" else v


def is_resolved_tracking_adequate(body: str) -> bool:
    decls = parse_declarations(body)
    ls = find_last_decl(decls, "letter-spacing")
    if not ls:
        return False
    m = re.match(r"^(-?\d*\.?\d+)\s*(em|px|rem)\b", ls[1], re.I)
    if not m:
        return False
    v = float(m.group(1))
    unit = m.group(2).lower()
    if unit == "em":
        return v >= 0.06
    tracking_px = v * ROOT_FONT_PX if unit == "rem" else v
    fs_px = resolve_font_size_px(decls)
    if fs_px is not None:
        return fs_px > 0 and tracking_px >= fs_px * 0.06
    if any(d[0] == "font-size" for d in decls):
        return False
    return tracking_px >= 1


# ── indigo token-block stripping ──────────────────────────────────────────


def strip_token_blocks(html: str) -> str:
    def per_style(m: re.Match) -> str:
        return m.group(1) + strip_token_blocks_from_css(m.group(2)) + m.group(3)

    return re.sub(r"(<style[^>]*>)([\s\S]*?)(</style>)", per_style, html, flags=re.I)


def strip_token_blocks_from_css(css: str) -> str:
    cleaned = re.sub(r"/\*[\s\S]*?\*/", "", css)

    def per_rule(m: re.Match) -> str:
        selector, body = m.group(1), m.group(2)
        sel = selector.strip()
        if not selector_list_is_global_theme_scope(sel):
            return m.group(0)
        decls = [d.strip() for d in body.split(";") if d.strip()]
        if not decls:
            return m.group(0)
        if not all(is_token_shaped_declaration(d) for d in decls):
            return m.group(0)
        if any(declaration_launders_indigo(d) for d in decls):
            return m.group(0)
        return ""

    return re.sub(r"([^{}]*)\{([^{}]*)\}", per_rule, cleaned)


def declaration_launders_indigo(decl: str) -> bool:
    m = re.match(r"^(--[\w-]+)\s*:\s*(.+)$", decl)
    if not m:
        return False
    name, value = m.group(1).lower(), m.group(2).lower()
    if name == "--accent":
        return False
    return any(hexv in value for hexv in AI_DEFAULT_INDIGO)


def is_token_shaped_declaration(decl: str) -> bool:
    if re.match(r"^--[\w-]+\s*:", decl):
        return True
    if re.match(r"^color-scheme\s*:", decl, re.I):
        return True
    return False


TAG_ATTR_RE = re.compile(r"^(?::root|html|body)(?:\[([a-zA-Z-]+)(?:[*^$|~]?=[^\]]*)?\])?$")
BARE_ATTR_RE = re.compile(r"^\[([a-zA-Z-]+)(?:[*^$|~]?=[^\]]*)?\]$")


def is_global_theme_scope_selector(s: str) -> bool:
    m = TAG_ATTR_RE.match(s)
    if m:
        attr = m.group(1)
        return True if not attr else attr.lower() in GLOBAL_THEME_ATTRIBUTES
    m = BARE_ATTR_RE.match(s)
    if m and m.group(1).lower() in GLOBAL_THEME_ATTRIBUTES:
        return True
    return False


def selector_list_is_global_theme_scope(selector: str) -> bool:
    parts = [s.strip() for s in selector.split(",") if s.strip()]
    if not parts:
        return False
    return all(is_global_theme_scope_selector(s) for s in parts)


def is_bare_global_selector(s: str) -> bool:
    return s in (":root", "html", "body")


# ── misc helpers ──────────────────────────────────────────────────────────


def detect_blue_cyan_trust_gradient(html: str) -> str | None:
    for m in re.finditer(r"linear-gradient\([^)]*\)", html, re.I):
        grad = m.group(0).lower()
        has_blue = any(h in grad for h in TRUST_GRADIENT_BLUE_HEXES) or bool(re.search(r"\bblue\b", grad))
        has_cyan = any(h in grad for h in TRUST_GRADIENT_CYAN_HEXES) or bool(re.search(r"\bcyan\b", grad))
        if has_blue and has_cyan:
            return m.group(0)
    return None


def clip(s: str) -> str:
    trimmed = re.sub(r"\s+", " ", s or "").strip()
    return trimmed[:197] + "…" if len(trimmed) > 200 else trimmed


# ── CLI ───────────────────────────────────────────────────────────────────


SEVERITY_ORDER = {"P0": 0, "P1": 1, "P2": 2}


def main(argv: list[str]) -> int:
    files = [a for a in argv[1:] if not a.startswith("-")]
    if not files:
        print(__doc__.strip())
        return 2

    total_p0 = 0
    for path in files:
        p = Path(path)
        if not p.is_file():
            print(f"lint · {path}\n  skipped — file not found\n")
            continue
        findings = sorted(
            lint(p.read_text(encoding="utf-8")), key=lambda f: SEVERITY_ORDER[f.severity]
        )
        counts = {s: sum(1 for f in findings if f.severity == s) for s in ("P0", "P1", "P2")}
        total_p0 += counts["P0"]

        print(f"lint · {path}")
        for f in findings:
            print(f"  [{f.severity}] {f.id} — {f.message}")
            print(f"        fix: {f.fix}")
            if f.snippet:
                print(f"        near: `{f.snippet}`")
        if not findings:
            print("  clean — no findings.")
        verdict = "FAIL (fix P0 before shipping)" if counts["P0"] else "pass"
        print(f"  {counts['P0']} P0 · {counts['P1']} P1 · {counts['P2']} P2 — {verdict}\n")

    return 1 if total_p0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

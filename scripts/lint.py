#!/usr/bin/env python3
"""
Design Studio anti-slop linter.

Greppy, deterministic, no dependencies. It does NOT parse HTML — a finding
always includes a snippet so you can verify it. Rules mirror
references/quality-gates.md ("the seven cardinal sins" + soft tells), plus
computed WCAG contrast for the core token pairs and static accessibility
checks (alt text, labels, lang, zoom, focus, headings).

Usage:
    python3 scripts/lint.py artifact.html [more.html ...]
    python3 scripts/lint.py --json artifact.html        # machine-readable

Exit status: 1 if any P0 finding (must fix before delivery), else 0.
P0/P1/P2 meaning: see references/quality-gates.md.
"""

from __future__ import annotations

import json
import math
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

    # ── P0-4: hardcoded font-family bypassing --font-display ──────────
    m = DISPLAY_SANS_RE.search(html)
    if m:
        out.append(Finding(
            "P0", "sans-display",
            "A heading rule hardcodes Inter / Roboto / system-sans instead of using var(--font-display).",
            'Use `font-family: var(--font-display)` on h1/h2/h3 and bind the font stack in :root.',
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
    # Count each <svg>...</svg> schematic as at most 1 accent moment even if multiple
    # internal <path>/<polygon>/<circle> nodes reference var(--accent).
    body_for_accent = re.sub(
        r"<svg[\s\S]*?</svg>",
        lambda m: "var(--accent)" if "var(--accent)" in m.group(0) else "",
        style_stripped,
        flags=re.I,
    )
    accent_uses = len(re.findall(r"var\(--accent\)", body_for_accent))
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

    # ── P1-5: multi-section landing page lacking flagship visual craft ─
    if not slide_matches and len(sections) >= 3 and re.search(r'data-design-id\s*=\s*["\']hero', html, re.I):
        has_craft = bool(re.search(
            r'\b(bento-hairline|bento-visual|app-window|index-showcase|hero-stage)\b',
            style_stripped, re.I,
        ))
        if not has_craft:
            out.append(Finding(
                "P1", "missing-visual-craft",
                "Landing page has 3+ sections but lacks 2025–2026 visual product craft (.hero-stage, .app-window, .bento-hairline, .bento-visual, or .index-showcase).",
                "Anchor the hero with a multi-pane .app-window or telemetry stage, and use .bento-hairline with .bento-visual SVG schematics or .index-showcase for features instead of plain-text icon grids.",
            ))

    # ── P1-6: dashboard lacking KPI row + data visualization ──────────
    # Token-exact class matching: "agent-shell" must NOT count as "shell".
    class_tokens: set[str] = set()
    for cm in re.finditer(r"""\bclass\s*=\s*["']([^"']*)["']""", html, re.I):
        class_tokens.update(cm.group(1).split())
    is_dashboard = bool(
        class_tokens & {"shell", "side", "topbar", "kpis", "kpi"}
        or re.search(r'data-design-id\s*=\s*["\']kpis["\']', html, re.I)
    )
    if is_dashboard and not slide_matches:
        has_kpi = bool(re.search(
            r'class="[^"]*\bkpis?\b[^"]*"|data-design-id\s*=\s*["\']kpis["\']',
            html, re.I,
        ))
        has_viz = bool(re.search(r"<svg\b", html, re.I)) or bool(re.search(r"<table\b", html, re.I))
        if not (has_kpi and has_viz):
            missing = []
            if not has_kpi:
                missing.append("KPI row (.kpis/.kpi)")
            if not has_viz:
                missing.append("inline SVG chart or data table")
            out.append(Finding(
                "P1", "dashboard-missing-craft",
                f"Dashboard lacks {', '.join(missing)} — dashboards need a KPI strip plus at least one chart or table.",
                "Add a gapless .kpis strip (label + mono tabular-nums value + delta) and a primary inline-SVG chart or dense data table per references/artifact-contract.md.",
            ))

    # ── P0/P1: accessibility statics + computed contrast ──────────────
    out.extend(check_a11y(html))
    contrast_findings, _ = check_contrast(html)
    out.extend(contrast_findings)

    # ── Agent screens (only when data-artifact="agent") ────────────────
    if re.search(r'data-artifact\s*=\s*["\']agent["\']', html, re.I):
        out.extend(check_agent(html))

    return out


# ── agent-screen checks (references/agent-ux.md) ──────────────────────────

AGENT_STATUSES = {"queued", "running", "success", "error", "cancelled"}
CLOSERS_RE = r"</(?:div|section|article|form|aside|main)\b[^>]*>"
OUTPUT_RE = r"<(?:details|pre)\b[^>]*>|<code\b[^>]*>|\bdata-output\b|class\s*=\s*[\"'][^\"']*\b(?:output|preview)\b"


def _norm_token(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _element_span(body: str, open_start: int) -> tuple[int, int]:
    """Best-effort (start, end) of the element opening at open_start."""
    m = re.match(r"<([a-zA-Z][a-zA-Z0-9]*)", body[open_start:])
    if not m:
        return (open_start, open_start)
    tag = m.group(1).lower()
    open_end = body.find(">", open_start)
    if open_end == -1:
        return (open_start, len(body))
    if body[open_end - 1] == "/":
        return (open_start, open_end + 1)
    depth = 1
    pat = re.compile(r"</?%s\b[^>]*>" % tag, re.I)
    for tm in pat.finditer(body, open_end + 1):
        t = tm.group(0)
        if t.startswith("</"):
            depth -= 1
        elif not t.endswith("/>"):
            depth += 1
        if depth == 0:
            return (open_start, tm.end())
    return (open_start, len(body))


def check_agent(html: str) -> list[Finding]:
    """P0/P1 contracts for agent thread/run/approval/activity screens."""
    out: list[Finding] = []
    body = re.sub(r"<!--[\s\S]*?-->", "", html)

    # ── P0: every [data-tool-call] needs data-status + data-latency ────
    for m in re.finditer(r"<[^>]+\bdata-tool-call\s*=\s*[\"']([^\"']+)[\"'][^>]*>", body, re.I):
        tag, name = m.group(0), m.group(1)
        status = re.search(r"""\bdata-status\s*=\s*["']([^"']+)["']""", tag, re.I)
        latency = re.search(r"""\bdata-latency\s*=\s*["']([^"']*)["']""", tag, re.I)
        problems = []
        if not status or status.group(1).lower() not in AGENT_STATUSES:
            problems.append("data-status (queued/running/success/error/cancelled)")
        if latency is None or not latency.group(1).strip():
            problems.append("data-latency")
        if problems:
            out.append(Finding(
                "P0", "tool-call-missing-status",
                f'Tool call "{name}" is missing {" and ".join(problems)}.',
                'Add data-status="queued|running|success|error|cancelled" and data-latency="412ms" (use "—" when not started) plus a visible status + latency pill.',
                clip(tag),
            ))

    # ── P0: every [data-destructive] needs an approval control ─────────
    approvals = {
        m.group(1) for m in
        re.finditer(r"""\bdata-approval\s*=\s*["']([^"']+)["']""", body, re.I)
    }
    approval_opens = [m.start() for m in re.finditer(r"<[^>]+\bdata-approval(?:\s*=|\s|>|/>)", body, re.I)]
    for m in re.finditer(r"<[^>]+\bdata-destructive(?:\s*=\s*[\"'][^\"']*[\"'])?[^>]*>", body, re.I):
        tag = m.group(0)
        ref = re.search(r"""\bdata-approval-for\s*=\s*["']([^"']+)["']""", tag, re.I)
        inside = any(
            open_pos < m.start() and not re.search(CLOSERS_RE, body[open_pos:m.start()], re.I)
            for open_pos in approval_opens
        )
        if (ref and ref.group(1) in approvals) or inside:
            continue
        out.append(Finding(
            "P0", "destructive-without-approval",
            "A destructive action has no approval control — irreversible actions need Approve/Reject/Edit.",
            'Place it inside a [data-approval] block, or point it at one with data-approval-for="plan-id" matching a data-approval="plan-id".',
            clip(tag),
        ))

    # ── P0: every [data-run] needs a Stop/Cancel control ──────────────
    for m in re.finditer(r"<[^>]+\bdata-run(?:\s*=\s*[\"'][^\"']*[\"'])?[^>]*>", body, re.I):
        _, end = _element_span(body, m.start())
        if not re.search(r"""\bdata-run-control\s*=\s*["']stop["']""", body[m.start():end], re.I):
            out.append(Finding(
                "P0", "run-missing-stop",
                "A run view ([data-run]) has no Stop/Cancel control — long runs need an exit.",
                'Add <button type="button" data-run-control="stop">Stop run</button> to the run header, next to elapsed time, tokens, and cost.',
                clip(m.group(0)),
            ))

    # ── P0: destructive approve buttons must name the action ───────────
    for m in re.finditer(
        r"<[^>]+\bdata-destructive(?:\s*=\s*[\"']([^\"']*)[\"'])?[^>]*>", body, re.I,
    ):
        target = _norm_token(m.group(1) or "")
        if not target:
            continue
        d_start, _ = _element_span(body, m.start())
        # enclosing approval block: nearest data-approval open whose span holds us
        block = None
        for am in re.finditer(r"<[^>]+\bdata-approval(?:\s*=|\s|>|/>)", body, re.I):
            a_start, a_end = _element_span(body, am.start())
            if a_start <= m.start() < a_end:
                block = body[a_start:a_end]
                break
        named = False
        if block:
            for bm in re.finditer(
                r"<button\b([^>]*)>([\s\S]*?)</button>", block, re.I,
            ):
                attrs, text = bm.group(1), re.sub(r"<[^>]+>", "", bm.group(2))
                if not re.search(r"approv", text, re.I):
                    continue
                label = re.search(r"""\baria-label\s*=\s*["']([^"']+)["']""", attrs, re.I)
                name = label.group(1) if label else text
                if target in _norm_token(name):
                    named = True
                    break
        if not named:
            out.append(Finding(
                "P0", "destructive-approve-unnamed",
                "A destructive action's approve button does not name the action — approvers must see what they approve.",
                'Name the target in the button, e.g. <button aria-label="Approve and restart checkout-api-02">Approve & restart checkout-api-02</button>.',
                clip(m.group(0)),
            ))

    # ── P1: every active tool call needs an output/preview region ──────
    for m in re.finditer(r"<[^>]+\bdata-tool-call\s*=\s*[\"']([^\"']+)[\"'][^>]*>", body, re.I):
        tag, name = m.group(0), m.group(1)
        status = re.search(r"""\bdata-status\s*=\s*["']([^"']+)["']""", tag, re.I)
        if status and status.group(1).lower() in {"queued", "cancelled"}:
            continue
        _, end = _element_span(body, m.start())
        if not re.search(OUTPUT_RE, body[m.start():end], re.I):
            out.append(Finding(
                "P1", "tool-call-missing-output",
                f'Tool call "{name}" has no output/preview region — reviewers cannot verify the result.',
                "Add <details>Args/Output</details>, a <pre> excerpt, or a [data-output] block inside the card. Queued/cancelled calls are exempt.",
                clip(tag),
            ))

    # ── P1: accent budget on agent views (best-effort static count) ────
    accent_uses = 0
    for block in re.finditer(r"<style[^>]*>([\s\S]*?)</style>", body, re.I):
        css = re.sub(r"/\*[\s\S]*?\*/", "", block.group(1))
        css = re.sub(r":root\s*\{[^}]*\}", "", css)
        css = re.sub(r"color-mix\((?:[^()]*\([^()]*\))*[^()]*\)", "", css)
        css = re.sub(r"[^{}]*:focus-visible[^{]*\{[^}]*\}", "", css)
        accent_uses += len(re.findall(r"var\(--accent\)", css))
    if accent_uses > 2:
        out.append(Finding(
            "P1", "accent-overuse",
            f"var(--accent) fills/text on {accent_uses} declarations — agent views keep accent to 2 or fewer visible uses.",
            "Move success pills to the muted success tone (color-mix of --success), keep accent for the primary action and the current-step signal only.",
        ))

    # ── P1: streaming / working regions need aria-live ─────────────────
    # aria-live on an ancestor (e.g. the wrapping status <div>) counts.
    for m in re.finditer(
        r"<(p|div|span|section)([^>]*)>([^<]*?(?:Working|working|Streaming|streaming)[^<]*)</\1>",
        body,
    ):
        if re.search(r"""\baria-live\s*=""", m.group(2), re.I):
            continue
        ancestor_live = False
        for am in re.finditer(r"<(?:div|section)[^>]*\baria-live\s*=[^>]*>", body[:m.start()], re.I):
            if not re.search(CLOSERS_RE, body[am.end():m.end()], re.I):
                ancestor_live = True
                break
        if not ancestor_live:
            out.append(Finding(
                "P1", "stream-missing-aria-live",
                "A streaming/working region lacks aria-live — screen readers never hear status changes.",
                'Add aria-live="polite" to the streaming message or status line.',
                clip(m.group(0)),
            ))
            break

    return out


# ── CSS helpers (uppercase-tracking check, token scopes) ──────────────────


def extract_css_tokens(html: str) -> list[dict]:
    scopes: list[dict] = []
    # strip HTML comments first — artifact headers describe the file and often
    # mention "<style>", which would otherwise hijack the style-block regex
    html = re.sub(r"<!--[\s\S]*?-->", "", html)
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


# ── accessibility statics ──────────────────────────────────────────────────


def check_a11y(html: str) -> list[Finding]:
    """Static accessibility checks that grep can genuinely decide."""
    out: list[Finding] = []

    # P0: <html> without a lang attribute
    hm = re.search(r"<html\b([^>]*)>", html, re.I)
    if hm and not re.search(r"\blang\s*=", hm.group(1), re.I):
        out.append(Finding(
            "P0", "lang-missing",
            "<html> has no lang attribute — screen readers have to guess the language.",
            'Add lang="en" (or the artifact\'s language) to the <html> tag.',
            clip(hm.group(0)),
        ))

    # P1: pinch-zoom blocked
    vm = re.search(r"""<meta[^>]+name\s*=\s*["']viewport["'][^>]*>""", html, re.I)
    if vm and re.search(r"(user-scalable\s*=\s*no|maximum-scale\s*=\s*1(\.0*)?\b)", vm.group(0), re.I):
        out.append(Finding(
            "P1", "zoom-blocked",
            "Viewport blocks pinch-zoom (user-scalable=no / maximum-scale=1).",
            "Remove both from the viewport meta — blocking zoom breaks low-vision users.",
            clip(vm.group(0)),
        ))

    # P0: <img> without alt
    no_alt = [
        t for t in re.findall(r"<img\b[^>]*>", html, re.I)
        if not re.search(r"\balt\s*=", t, re.I)
    ]
    if no_alt:
        out.append(Finding(
            "P0", "img-alt",
            f"{len(no_alt)} <img> tag(s) without an alt attribute.",
            'Add alt="description" for meaningful images or alt="" for decorative ones.',
            clip(no_alt[0]),
        ))

    # P0: form controls without a label
    fields = re.findall(r"<(?:input|textarea|select)\b[^>]*>", html, re.I)
    for_labels = set(re.findall(r"""<label[^>]*\bfor\s*=\s*["']([^"']+)["']""", html, re.I))
    label_blocks = re.findall(r"<label\b[\s\S]*?</label>", html, re.I)
    unlabeled: list[str] = []
    for tag in fields:
        if re.search(r"""\btype\s*=\s*["']?(hidden|submit|button|reset|image)\b""", tag, re.I):
            continue
        if re.search(r"\baria-label(?:ledby)?\s*=", tag, re.I):
            continue
        idm = re.search(r"""\bid\s*=\s*["']([^"']+)["']""", tag)
        if idm and idm.group(1) in for_labels:
            continue
        if any(tag in block for block in label_blocks):
            continue
        unlabeled.append(tag)
    if unlabeled:
        out.append(Finding(
            "P0", "input-unlabeled",
            f"{len(unlabeled)} form control(s) without a label or aria-label.",
            'Pair each control with <label for="id">, aria-label, or wrap it in a <label> element.',
            clip(unlabeled[0]),
        ))

    # heading structure — full documents only; fragment files get a pass
    if re.search(r"<html\b", html, re.I):
        h1s = len(re.findall(r"<h1\b", html, re.I))
        if h1s != 1:
            out.append(Finding(
                "P1", "heading-structure",
                f"Found {h1s} <h1> element(s) — a page needs exactly one top-level heading.",
                "Keep one <h1> (the page or artifact title) and demote the rest to h2/h3, in order.",
            ))
        levels = [int(m) for m in re.findall(r"<h([1-6])\b", html, re.I)]
        for prev, cur in zip(levels, levels[1:]):
            if cur > prev + 1:
                out.append(Finding(
                    "P2", "heading-order",
                    f"Heading order skips a level (h{prev} to h{cur}) — breaks screen-reader outlines.",
                    f"Insert an h{prev + 1} in between, or demote the h{cur}.",
                ))
                break

    # P1: justified text (hard to read on the web)
    if re.search(r"text-align\s*:\s*justify", html, re.I):
        out.append(Finding(
            "P1", "justify-text",
            "text-align: justify detected — rivers of whitespace, worst at small sizes.",
            "Use left-aligned text (the default). Justification is a print habit.",
        ))

    # P1: focus outlines removed without a replacement
    css = "".join(m.group(1) for m in re.finditer(r"<style[^>]*>([\s\S]*?)</style>", html, re.I))
    css = re.sub(r"/\*[\s\S]*?\*/", "", css)
    if re.search(r"outline\s*:\s*(none|0)\b", css, re.I) and not re.search(r":focus-visible", css, re.I):
        out.append(Finding(
            "P1", "focus-removed",
            "An outline is removed but no :focus-visible replacement exists.",
            "Never remove focus rings without replacement — add a :focus-visible ring (2px accent, 2px offset) on every interactive element.",
        ))

    return out


# ── color parsing & computed WCAG contrast ────────────────────────────────

WCAG_TEXT_MIN = 4.5
WCAG_LARGE_MIN = 3.0

# (foreground token, background token, is-primary-text, description)
CONTRAST_PAIRS: list[tuple[str, str, bool, str]] = [
    ("fg", "bg", True, "primary text on the page background"),
    ("fg", "surface", True, "primary text on cards / surfaces"),
    ("muted", "bg", False, "secondary text on the background"),
    ("muted", "surface", False, "secondary text on surfaces"),
    ("accent", "bg", False, "accent text on the background"),
    ("accent", "surface", False, "accent text on surfaces"),
    ("accent-on", "accent", False, "label text on the accent fill"),
]


def _srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def parse_color(value: str) -> tuple[float, float, float] | None:
    """Parse hex / oklch() / rgb() to LINEAR sRGB components. None if unsupported."""
    v = value.strip().lower()

    m = re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})(?:[0-9a-f]{2})?", v)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(ch * 2 for ch in h)
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        return (_srgb_to_linear(r), _srgb_to_linear(g), _srgb_to_linear(b))

    m = re.fullmatch(r"oklch\(\s*([\d.]+)(%?)\s+([\d.]+)\s+([\d.]+)(?:deg)?\s*\)", v)
    if m:
        L = float(m.group(1)) / (100 if m.group(2) == "%" else 1)
        C, hue = float(m.group(3)), float(m.group(4))
        rad = hue * math.pi / 180.0
        a, b = C * math.cos(rad), C * math.sin(rad)
        l_ = L + 0.3963377774 * a + 0.2158037573 * b
        m_ = L - 0.1055613458 * a - 0.0638541728 * b
        s_ = L - 0.0894841775 * a - 1.2914855480 * b
        l, mm, s = l_ ** 3, m_ ** 3, s_ ** 3
        r = 4.0767416621 * l - 3.3077115913 * mm + 0.2309699292 * s
        g = -1.2684380046 * l + 2.6097574011 * mm - 0.3413193965 * s
        bb = -0.0041960863 * l - 0.7034186147 * mm + 1.7076147010 * s
        return (min(1.0, max(0.0, r)), min(1.0, max(0.0, g)), min(1.0, max(0.0, bb)))

    m = re.fullmatch(r"rgb\(\s*(\d+)[\s,]+(\d+)[\s,]+(\d+)\s*\)", v)
    if m:
        r, g, b = (int(x) / 255 for x in m.groups())
        return (_srgb_to_linear(r), _srgb_to_linear(g), _srgb_to_linear(b))

    return None


def relative_luminance(rgb: tuple[float, float, float]) -> float:
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(rgb1: tuple[float, float, float], rgb2: tuple[float, float, float]) -> float:
    l1, l2 = relative_luminance(rgb1), relative_luminance(rgb2)
    if l2 > l1:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def check_contrast(html: str) -> tuple[list[Finding], str | None]:
    """Compute WCAG ratios for the core token pairs from the :root block(s).

    Returns findings plus a one-line summary for the CLI/JSON output. Findings
    fire only below 3:1 (genuinely unreadable). Ratios between 3:1 and 4.5:1
    are reported in the summary as "large/UI only" — small text at those
    ratios needs a darker shade, which is a design decision, not a lint
    violation.
    """
    scopes = extract_css_tokens(html)
    if not scopes:
        return [], None
    themes = build_resolved_themes(scopes)
    findings: list[Finding] = []
    parts: list[str] = []
    for t_idx, tmap in enumerate(themes):
        for a_name, b_name, is_primary, label in CONTRAST_PAIRS:
            key_a, key_b = f"--{a_name}", f"--{b_name}"
            if key_a not in tmap or key_b not in tmap:
                continue
            c1 = parse_color(resolve_css_vars(tmap[key_a], tmap))
            c2 = parse_color(resolve_css_vars(tmap[key_b], tmap))
            if not c1 or not c2:
                continue
            ratio = contrast_ratio(c1, c2)
            theme_note = "" if t_idx == 0 else f" (theme {t_idx + 1})"
            pair = f"{a_name}/{b_name}{theme_note}"
            if ratio < WCAG_LARGE_MIN or (is_primary and ratio < WCAG_TEXT_MIN):
                findings.append(Finding(
                    "P1", "contrast-text",
                    f"Contrast {pair} = {ratio:.1f}:1 — {label} is below the readable minimum.",
                    "Darken the lighter side of the pair (or lighten it on dark themes). "
                    "Body text needs 4.5:1; large text (24px+, or 18.7px+ bold) needs 3:1.",
                ))
                parts.append(f"{pair} {ratio:.1f}:1 ✗")
            elif ratio < WCAG_TEXT_MIN:
                parts.append(f"{pair} {ratio:.1f}:1 (large/UI only)")
            else:
                parts.append(f"{pair} {ratio:.1f}:1 ✓")
    summary = " · ".join(parts) if parts else None
    return findings, summary


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
    as_json = "--json" in argv
    files = [a for a in argv[1:] if not a.startswith("-")]
    if not files:
        print(__doc__.strip())
        return 2

    total_p0 = 0
    report: list[dict] = []
    for path in files:
        p = Path(path)
        if not p.is_file():
            if as_json:
                report.append({"path": path, "error": "file not found"})
            else:
                print(f"lint · {path}\n  skipped — file not found\n")
            continue
        raw = p.read_text(encoding="utf-8")
        findings = sorted(lint(raw), key=lambda f: SEVERITY_ORDER[f.severity])
        counts = {s: sum(1 for f in findings if f.severity == s) for s in ("P0", "P1", "P2")}
        total_p0 += counts["P0"]
        _, contrast = check_contrast(raw)

        if as_json:
            report.append({
                "path": path,
                "counts": counts,
                "contrast": contrast,
                "findings": [
                    {"severity": f.severity, "id": f.id, "message": f.message,
                     "fix": f.fix, "snippet": f.snippet}
                    for f in findings
                ],
            })
            continue

        print(f"lint · {path}")
        for f in findings:
            print(f"  [{f.severity}] {f.id} — {f.message}")
            print(f"        fix: {f.fix}")
            if f.snippet:
                print(f"        near: `{f.snippet}`")
        if not findings:
            print("  clean — no findings.")
        if contrast:
            print(f"  contrast: {contrast}")
        verdict = "FAIL (fix P0 before shipping)" if counts["P0"] else "pass"
        print(f"  {counts['P0']} P0 · {counts['P1']} P1 · {counts['P2']} P2 — {verdict}\n")

    if as_json:
        print(json.dumps({"files": report, "total_p0": total_p0}, indent=2))

    return 1 if total_p0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

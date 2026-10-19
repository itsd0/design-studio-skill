#!/usr/bin/env python3
"""
Compose a paste-ready fragment into a seed page.

`assets/section-skeletons.html` (and friends) ship as fragments: they have
markup but no stylesheet, because every class they use is defined by the
seed they get pasted into. Rendering a fragment on its own proves nothing.

This tool pastes a fragment into a seed's <main id="content"> so the result
can be rendered and verified as a real page.

Usage:
    python3 tests/compose.py <seed.html> <fragment.html> > composed.html
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

OPEN_RE = re.compile(r'<main\b[^>]*\bid=["\']content["\'][^>]*>', re.I)
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)


def strip_leading_comment(html: str) -> str:
    """Drop a leading <!-- ... --> block (the fragment's own instructions)."""
    m = re.match(r"\s*<!--.*?-->\s*", html, re.S)
    return html[m.end():] if m else html


def find_main(html: str) -> tuple[int, int, int] | None:
    """Locate <main id="content">…</main>, ignoring matches inside comments.

    Returns (open_end, close_start, close_end) offsets.
    """
    comments = [(m.start(), m.end()) for m in COMMENT_RE.finditer(html)]
    for m in OPEN_RE.finditer(html):
        if any(s <= m.start() < e for s, e in comments):
            continue  # the tag only appears inside a comment block
        close = html.find("</main>", m.end())
        if close == -1:
            return None
        return m.end(), close, close + len("</main>")
    return None


def compose(seed_html: str, fragment_html: str) -> str:
    span = find_main(seed_html)
    if not span:
        raise ValueError('seed has no <main id="content"> to compose into')
    open_end, close_start, close_end = span
    body = strip_leading_comment(fragment_html).strip()
    return seed_html[:open_end] + "\n" + body + "\n" + seed_html[close_start:close_end] + \
        seed_html[close_end:]


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip())
        return 2
    seed = Path(argv[1]).read_text(encoding="utf-8")
    fragment = Path(argv[2]).read_text(encoding="utf-8")
    sys.stdout.write(compose(seed, fragment))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

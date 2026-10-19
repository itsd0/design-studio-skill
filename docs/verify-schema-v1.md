# Verify `--json` schema v1 (frozen)

`python3 scripts/verify.py --json <file>…` is a stable integration contract
as of v1.5.0. CI pipelines and editor extensions may parse it. Changes are
**additive-only**: new finding ids and new optional keys may appear; existing
keys are never renamed, removed, or retyped.

This is a *separate* contract from the lint schema (`docs/lint-schema-v1.md`).
The linter reads source; the verifier reads the rendered page. They never
share a file, and a change to one never retypes the other's keys.

## Top-level shape

```json
{
  "files": [
    {
      "path": "index.html",
      "error": "",
      "skipped": "",
      "counts": { "P0": 0, "P1": 0, "P2": 0 },
      "viewports": [
        {
          "viewport": "390x844",
          "measured": { "w": 390, "inner": 390, "h": 844, "dpr": 1 },
          "doc": { "scrollWidth": 390, "clientWidth": 390, "bodyScrollWidth": 390 },
          "counts": { "elements": 393, "textNodes": 210 },
          "contrastSkipped": 0,
          "late": true,
          "framed": true
        }
      ],
      "findings": [
        {
          "severity": "P0",
          "id": "overflow-element",
          "message": "`div.row` extends 10px past the 390x844 viewport.",
          "fix": "Constrain the element — the page scrolls sideways and the layout breaks on mobile.",
          "selector": "div.row",
          "detail": "GitHub Install Skill",
          "viewports": ["390x844"]
        }
      ]
    }
  ],
  "total_p0": 0,
  "total_p1": 0,
  "total_p2": 0
}
```

| Key | Type | Notes |
|---|---|---|
| `files[].path` | string | Echo of the CLI argument |
| `files[].error` | string | Set when the page could not be rendered at all; `""` otherwise |
| `files[].skipped` | string | Set when the file was not rendered (e.g. a paste-ready fragment with no stylesheet); `""` otherwise |
| `files[].counts` | object | Integer counts per severity; keys always `P0`, `P1`, `P2` |
| `files[].viewports` | array | One entry per rendered viewport, in the order requested |
| `files[].findings` | array | Sorted P0 → P2; empty array means clean |
| `total_p0` | integer | Sum of P0 findings; mirrors the process exit code (`1` iff `> 0`) |
| `total_p1` | integer | Sum of P1 findings |
| `total_p2` | integer | Sum of P2 findings |

## Viewport shape

| Key | Type | Notes |
|---|---|---|
| `viewport` | string | The requested size, e.g. `"390x844"` |
| `measured.w` | integer | Layout viewport width in CSS px (what media queries saw) |
| `measured.inner` | integer | `window.innerWidth` (layout width plus any classic scrollbar) |
| `measured.h` | integer | Viewport height in CSS px |
| `measured.dpr` | number | Device pixel ratio |
| `doc.scrollWidth` | integer | Document content width — the horizontal-overflow signal |
| `doc.clientWidth` | integer | Layout viewport width |
| `counts.elements` | integer | Elements inspected |
| `counts.textNodes` | integer | Text-bearing elements measured for contrast |
| `contrastSkipped` | integer | Text runs skipped because a background image made the contrast unknowable |
| `late` | boolean | `true` when measured after `load` + `document.fonts.ready` |
| `framed` | boolean | `true` when the measured width matched the requested width |

## Finding shape

| Key | Type | Notes |
|---|---|---|
| `severity` | `"P0"` \| `"P1"` \| `"P2"` | P0 fails the build |
| `id` | string | Stable kebab-case rule id (e.g. `text-clipped`) |
| `message` | string | Human-readable, may be reworded between releases |
| `fix` | string | Suggested remediation, may be reworded |
| `selector` | string | CSS selector of the offending element; `""` for page-level findings |
| `detail` | string | Offending text or URL; `""` when not applicable |
| `viewports` | array | Viewport labels the finding appeared in |

Only `severity` and `id` are safe to match on programmatically; treat
`message`, `fix`, `selector`, and `detail` as display strings. A test in
`tests/run_tests.py` (`run_verify_schema`) pins this shape.

## Rule ids

| id | Severity | Meaning |
|---|---|---|
| `probe-failed` | P0 | The in-page probe did not run — the artifact throws during load |
| `runtime-error` | P0 | Uncaught JS error or `console.error` during load |
| `overflow-x` | P0 | The document scrolls horizontally at that viewport |
| `overflow-element` | P0 | An element extends past its frame (viewport, or slide for decks) |
| `text-clipped` | P0 | Content is cut off by an `overflow: hidden` box, with no ellipsis |
| `contrast-text` | P0 | Rendered text below its WCAG AA ratio (4.5:1, or 3:1 for large text) |
| `min-content-overflow` | P0 | An element's min-content width exceeds the space available — it overflows, and a wider font fallback will make it worse |
| `tap-target-small` | P1 | Interactive target under 24×24 CSS px, with no inline or spacing exception |
| `tight-fit` | P1 | A layout that fits with under 3% to spare — a slightly wider font fallback will push it over |
| `img-missing-dimensions` | P1 | `<img>` without intrinsic `width`/`height` — layout shift on load |
| `focus-style-missing` | P1 | No `:focus` / `:focus-visible` rule ships with the artifact |
| `focus-indicator-removed` | P1 | Focus rules remove the indicator without replacing it |
| `viewport-meta-missing` | P1 | No `<meta name="viewport">` |
| `zoom-blocked` | P1 | The viewport meta blocks zoom |
| `text-truncated` | P2 | Text is truncated with an ellipsis — confirm the full value is reachable |

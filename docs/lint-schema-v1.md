# Lint `--json` schema v1 (frozen)

`python3 scripts/lint.py --json <file>…` is a stable integration contract as of
v1.4.0. CI pipelines and editor extensions may parse it. Changes are
**additive-only**: new finding ids and new optional keys may appear; existing
keys are never renamed, removed, or retyped.

## Top-level shape

```json
{
  "files": [
    {
      "path": "index.html",
      "counts": { "P0": 0, "P1": 0, "P2": 0 },
      "contrast": "fg/bg 17.9:1 ✓ · …",
      "findings": [ { "severity": "P0", "id": "purple-gradient", "message": "…", "fix": "…", "snippet": "…" } ]
    }
  ],
  "total_p0": 0
}
```

| Key | Type | Notes |
|---|---|---|
| `files[].path` | string | Echo of the CLI argument |
| `files[].counts` | object | Integer counts per severity; keys always `P0`, `P1`, `P2` |
| `files[].contrast` | string \| null | Human-readable pair ratios; `null` when no token block found |
| `files[].findings` | array | Sorted P0 → P2; empty array means clean |
| `files[].error` | string | *Instead of* the above keys when the file is missing |
| `total_p0` | integer | Sum of P0 findings; mirrors the process exit code (`1` iff `> 0`) |

## Finding shape

| Key | Type | Notes |
|---|---|---|
| `severity` | `"P0"` \| `"P1"` \| `"P2"` | P0 fails the build |
| `id` | string | Stable kebab-case rule id (e.g. `tool-call-missing-status`) |
| `message` | string | Human-readable, may be reworded between releases |
| `fix` | string | Suggested remediation, may be reworded |
| `snippet` | string | Offending excerpt, `""` when not applicable |

Only `severity` and `id` are safe to match on programmatically; treat
`message`, `fix`, and `snippet` as display strings. A test in
`tests/run_tests.py` (`run_schema`) pins this shape.

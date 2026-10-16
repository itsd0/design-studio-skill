# Data visualization — charts that argue honestly

Charts are hand-rolled inline SVG (no libraries). This is the craft contract for anything resembling a chart, sparkline, KPI card, or data table.

## Pick the form before drawing the form

| The story | Form | Notes |
|---|---|---|
| Change over time | line, 2–4 series max | area only for a single series |
| Compare categories | horizontal bar, sorted | sorted by value, never alphabetically |
| Progress toward a goal | big number + delta (bullet) | not a gauge |
| Part of a whole | stacked bar, ≤ 4 segments | pie/donut only if ≤ 3 slices and one dominates |
| Distribution | histogram or dot strip | show the median line |
| Correlation | scatter, ≤ 200 points | no trend line unless actually fitted |
| One value vs its normal range | sparkline + band | the range is the point |

One chart answers one question. If the title needs "and", it is two charts.

## Axes, gridlines, labels

- Bars start at zero. Always. A truncated bar axis is a lie. (Lines may truncate if clearly labeled.)
- One y-axis. Dual axes are for impressing, not informing.
- 3–5 ticks, round numbers, no decimals unless the data needs them.
- Gridlines: horizontal only, hairline (`var(--border)`), behind the data. No vertical grids unless it's a time ruler.
- De-emphasize everything that isn't data: axis labels `--muted`, 12px mono.
- With ≤ 3 series, label directly in the plot (name at the end of the line); legends only when direct labels collide.
- Units appear once — in the axis title or the value, never repeated per tick.
- Rounding: 1 decimal max, thousands separators, consistent abbreviation (12.4k).

## The accent's job

- Context series: neutral (`--fg` at 100 / 70 / 45% opacity). **The accent highlights exactly one thing** — the series that makes the point, the current period, the crossed threshold.
- Never a rainbow. Max 4 series; prefer position + opacity steps over new hues.
- Red/green only for status **with a text label attached** — colorblind-safe by construction.
- No gradients on series, no drop shadows, no 3-D, no decorative chart frames.

## KPI card formula

```
label (small, muted) → value (display size, mono, tabular-nums) → delta (mono: sign + text + comparison period)
```

- A delta without a comparison period ("+12% since when?") is noise.
- Delta color is semantic or muted — never the accent. The value itself earns the accent at most once per dashboard.
- One supporting line max. If it needs three, it is a chart, not a card.

## Inline SVG conventions

- `viewBox="0 0 W H"` with explicit `width`/`height` or CSS sizing. `preserveAspectRatio="none"` on a chart is banned — it lies about slopes.
- Coordinates rounded to 1 decimal; raw numbers live in the markup (no JS to compute charts).
- `<polyline>` / `<path>` for lines, `<rect>` for bars, `<circle>` for ≤ 12 points. Data stroke-width 2; axis 1.
- In-SVG text uses `font-family: var(--font-mono)`.
- Accessibility: `<svg role="img">` plus `<title>` or `aria-label` stating the takeaway ("Transfers per week, up 18%") — never a bare chart.

Line chart skeleton:

```html
<figure>
  <svg viewBox="0 0 640 240" role="img" aria-label="[REPLACE · the takeaway]">
    <g stroke="var(--border)" stroke-width="1">
      <line x1="48" y1="40"  x2="620" y2="40"/>
      <line x1="48" y1="105" x2="620" y2="105"/>
      <line x1="48" y1="170" x2="620" y2="170"/>
    </g>
    <polyline points="48,152 172,140 296,146 420,108 544,96 620,64"
              fill="none" stroke="var(--accent)" stroke-width="2"
              stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
  <figcaption class="meta">[REPLACE · what changed, period]</figcaption>
</figure>
```

## Tables are charts too

- Numeric columns right-aligned, mono, tabular-nums; text left. Nothing centered.
- Every sortable column shows a sort affordance; the active column is marked.
- Hairline rules, no zebra striping; hover rows (`--fg-soft`); selected state visually distinct from hover.
- Row-count honesty: "Showing 1–20 of 214" — never a silently truncated list.
- Status cells carry text + dot, not hue alone; deltas carry signs; links look like links.

## Verification

- **Squint test:** blur the chart — the point should still be visible. If not, the wrong series got the accent.
- **Grayscale test:** everything remains readable without hue.
- **Zero test:** every bar starts at zero, every number rounds consistently, every unit appears once.

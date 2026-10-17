# Agent UX — pattern catalog for AI-agent product screens

Contracts for the `agent` artifact kind (`thread` · `run-detail` · `approval` · `activity`). Every pattern binds the active `:root` tokens verbatim, uses `var(--font-mono)` for tool names, latency, and status, and ships its empty / loading / error / interrupted / permission-denied states per `references/ux-flows.md`. Placeholders stay labeled (`[REPLACE · label]`) — never invent tool names, costs, or eval scores.

## 1 · Tool-call card `[data-tool-call]`

Required attributes: `data-status="queued|running|success|error|cancelled"` and `data-latency` (e.g. `data-latency="412ms"`). Required visible parts:

- Tool name in mono (`SENTRY_LIST_ISSUES`, `white-space: nowrap`), one-line purpose below it.
- Status pill + latency (`412ms`) on the same row — status is text, never color alone. Success pills use the muted success tone (`--success-muted`, a `color-mix()` of `--success`), keeping `--accent` within its 2-use budget.
- Args collapsible (`<details>`) plus an output preview (`<pre>` excerpt, `<details>`, or `[data-output]`). Queued/cancelled calls are exempt.
- Stacked cards keep a consistent gap — never touching borders.

States: `running` shows a reduced-motion-safe working indicator; `error` shows cause + retry; `cancelled` shows who cancelled; denied tools use the permission-denied block instead.

## 1b · Run header `[data-run]`

Every run view wraps in `[data-run]` with a header carrying a Stop/Cancel control plus elapsed time, tokens, and cost:

- `<button type="button" data-run-control="stop">Stop run</button>` next to `Elapsed [REPLACE · mm:ss] · [REPLACE · tokens] tokens · [REPLACE · cost]`. Unknown values stay labeled placeholders — never invent numbers.
- The linter fires P0 `run-missing-stop` when a run view lacks the control.

## 2 · Streaming message + thinking indicator

- Assistant message streams into a `aria-live="polite"` region; a separate `aria-live="polite"` status line announces `queued → running → success/error`.
- Thinking/working indicator: text label ("Working…") + skeleton matching the card shape. No emoji spinners.
- `prefers-reduced-motion`: no pulsing — static "Working…" text only.
- Interrupted: preserve partial output, show "Interrupted — resume or discard" with both buttons.

## 3 · Plan preview + approval `[data-approval]`

- Numbered steps (`01`–`04` via ordered list + CSS counters) with verb + object + target ("Restart `checkout-api-02`"). Steps are full hairline cards — never a colored left border (banned trope, see `references/quality-gates.md`); destructive steps get a tinted background plus an icon/label flag.
- Destructive steps carry `data-destructive="<target>"` and a visible flag ("Destructive — needs approval" with a warning icon).
- The approve button names the action: `Approve & restart checkout-api-02` (accessible label must contain the `data-destructive` target — P0 `destructive-approve-unnamed` otherwise). Destructive approvals use the neutral `.btn-destructive` treatment (surface fill, danger-tinted border), never the green success accent.
- Controls: Approve / Edit / Reject — all real `<button>`s, same visual weight so Reject stays equally reachable, keyboard operable, focus starts on the safe action. On mobile the approval bar sticks to the bottom (`position: sticky`) while the run awaits approval.
- Edit returns to thread with the plan quoted; Reject asks for a one-line reason (optional) and stops the run.
- Safe (non-destructive) plans may use an accent-fill primary button instead.

## 4 · Guardrail / policy warning

- One block per policy hit: icon + policy name, what was blocked, which policy, what to do next. Full `1px` hairline border plus a danger tint — never a colored left border.
- Never a toast when it needs a decision — inline banner or plan-step flag.
- Link to the policy or log, never a bare "Blocked".

## 4b · Live activity feed (timestamps + icons)

- Rows: status icon (inline SVG: check for done, alert for needs-review), action verb, unbroken object identifier (`white-space: nowrap` on `code`), status text, relative timestamp (`<time>2m ago</time>`), "View logs" link.
- `Auto-approved` vs `Needs review` is text, never hue alone.
- Live region `aria-live="polite"`; paused state when the user scrolls back ("3 new — jump to latest").

## 6 · Run DAG / timeline

- Nodes `SAVED → FORK → PROMPT → BUILD → EVAL` (domain-specific verbs allowed) with per-node `data-status`: done shows `✓` in a muted style, current takes the accent plus `aria-current="step"`, pending stays muted (`12px` mono minimum, ≥ 4.5:1). Hairline connector lines join the steps in order.
- Below 920px the timeline becomes a horizontally scrollable row (or a vertical list) — never a multi-column grid — so step order stays readable.
- Failed node shows error + retry; parallel lanes show lane labels.
- Failed node shows error + retry; parallel lanes show lane labels.
- Never invent durations — missing values render as `—` or `[REPLACE · p95]`.

## 7 · Eval receipt

- Checks passed/failed list, tokens, cost, duration — each with its comparison or source. Unknowns are `—`, never guessed.
- Failed checks link to the failing step; "Re-run eval" is a button.

## 8 · Screen compositions

| Screen | Layout (from `assets/agent-seed.html`) |
|---|---|
| `thread` | Main thread pane (messages + inline tool-call cards) + right inspector (selected tool I/O) |
| `run-detail` | Step DAG/timeline top, logs middle, eval receipt bottom |
| `approval` | Plan preview centered, Approve/Reject/Edit bar sticky, guardrail block above destructive steps |
| `activity` | Full-width live feed + filter (all / needs-review / errors) |

## 9 · Accessibility

- Streaming and status regions: `aria-live="polite"`.
- Approve/Reject/Edit: real buttons, Tab/Enter/Esc operable, visible `:focus-visible` ring.
- Focus management: opening approval moves focus to the dialog heading; closing returns focus to the invoking control.
- Status never conveyed by color alone — every dot carries a text label.
- Touch targets ≥ 44px; usable at 200% zoom; `prefers-reduced-motion` path ships with every animated pattern.

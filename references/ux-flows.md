# UX flows — the states and scripts every interface needs

A screen is never one state. Every data surface ships five: default, loading, empty, error, and partial. An artifact that renders only the happy default is a screenshot, not a product.

## The five states

| State | When | How it looks |
|---|---|---|
| Default | data present, nothing special | the design |
| Loading | first paint, > 300ms expected | skeleton matching the final shape; spinner only for an unknown shape |
| Empty | zero items | explain why + one action + one example. Never a blank void, never a shrug emoji |
| Error | fetch or validation failed | plain-language cause + recovery action + preserved input |
| Partial | some fields missing, more loading | render what exists, mark gaps explicitly ("—", "pending") |

Skeletons mimic the final layout (same blocks, same sizes) so the page doesn't jump when data lands.

## Empty state formula

1. What this space is ("Transfers appear here")
2. Why it's empty ("Nothing has been sent yet")
3. The one action ("Send your first file" — a real button, not a link)
4. Optional: one example or illustration in the artifact's visual language (no emoji, no stock 3-D character)

## Error formula

- Tell the user what happened in their language, not the system's ("We couldn't reach the server", not "ECONNREFUSED").
- Say what to do next; if a retry exists, it's a button on the error itself.
- Preserve everything the user typed or selected — errors never clear forms.
- Placement ladder: **inline** (field-level) → **banner** (page-level, needs a decision) → **toast** (transient confirmation only). Errors that need a decision never live in a toast.
- Never blame the user; never "Invalid input" without saying which input and why.

## Loading rules

- Delay skeletons ~200ms; below that the flash reads as jank.
- Once shown, keep minimum exposure ~300ms — a skeleton that blinks in and out is worse than a beat of empty.
- Only the region that's loading gets the skeleton — never a full-page overlay for a table refresh.

## Forms

- Label above the field, always visible; a placeholder is an example, never the label.
- Validate on blur and submit, not per keystroke (strength meters excepted).
- Error text sits directly under its field in the danger color, and the field border matches.
- Success needs no ceremony — clear the error and move on. Save the confetti.
- Long forms: labeled groups of 3–7 fields; progress affordance beyond two groups; an error summary at the top after submit.

## Confirmation & destructive actions

- Prefer undo over confirm: destructive action → toast with "Undo" for ~6s.
- When confirmation is unavoidable (irreversible, money, sharing), the dialog names the act and the object: "Delete 3 files?" with a danger-fill confirm — never "Are you sure? [OK]".
- Keyboard focus starts on the cancel action; destructive confirm is separated and last.
- Type-to-confirm only for project-level destruction.

## Navigation models (prototypes)

- **Hub / tabs:** 3–5 destinations, equal visual weight, current one marked. The default for app prototypes.
- **Stack:** back always returns to where the user came from. The back affordance sits top-left.
- **Detail views:** the title carries the object's identity ("transfer_08.csv", not "Details").
- Breadcrumbs only for hierarchies ≥ 3 levels; single pages and decks never get them.

## Microcopy bank

| Slot | Weak | Strong |
|---|---|---|
| Primary button | Submit | Create account |
| Secondary button | Cancel | Keep editing |
| Empty state | No data | No transfers yet — send your first file |
| Error | Something went wrong | We couldn't reach the server. Retry, or check your connection. |
| Loading | Loading... | Preparing your files (a skeleton beats this text) |
| Confirm | Are you sure? | Delete 3 files? This can't be undone. |
| Success toast | Operation successful | 3 files moved to Archive |

Rules: buttons say what happens; errors say what to do; empty states say what this is. No exclamation marks, and no "Oops", "Uh-oh", or "Whoops".

## Notification discipline

- One toast at a time (max 3 stacked), 4–6s, dismissible — never for anything requiring a decision.
- Toasts confirm or warn; banners persist until resolved; badges count.
- Never toast a success the user can already see — the row appearing is the feedback.

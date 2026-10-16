# UI patterns — overlays, menus, and the state machine every control owes

When you need a component, pick the **lightest layer** that fits. That ladder decides most of the argument before any styling happens.

## The overlay ladder

```
inline (text swap, field error) → disclosure (tooltip, popover) → menu (dropdown) → sheet / drawer → modal (dialog) → full-page takeover
```

Never skip a rung: a dropdown for two actions is a bug; a modal to pick a sort order is a cry for help.

Focus rules per layer:

- **Menus and popovers:** focus moves into the overlay; Esc closes and returns focus to the trigger; ↑/↓ move, Enter activates.
- **Modal:** focus trapped inside; Esc closes only the top-most layer; backdrop click closes only when nothing is unsaved; on close, focus returns to the trigger.
- **Drawers:** same contract as modal; an accidental overlay click must never discard the user's work.

## Buttons

- Hierarchy: primary (accent fill) / secondary (border) / ghost (text) / destructive (danger fill or danger text). **One primary per screen region** — accents are expensive.
- Every button defines default / hover / active / focus-visible / disabled. Focus ring: 2px `--accent`, 2px offset — never removed.
- Loading: spinner replaces the label, width stays fixed so layout never jumps.
- Labels are verb + object ("Send invoice"). "OK" is never a button.

## Menus (dropdowns)

- Items are verbs; 3–9 items; dividers group, they don't decorate.
- The destructive item goes last, separated, in the danger hue — and is still named specifically ("Delete transfer").
- Keyboard: ↑/↓ move, Enter runs, Esc returns to the trigger.

## Tabs vs segmented controls

- Tabs switch **views** (URL-worthy), ARIA tab pattern, ≤ 5. Segmented controls pick a **value** (filter, range). Pills/chips are tags and filters, not navigation.
- Active tab: fg color plus a 2px rule on the container edge — not a floating pill unless the design language demands it.

## Toasts

- Transient confirmations only: 4–6s, paused on hover, max 3 stacked, newest on top.
- Never toast an error that needs a decision — that's inline or a banner.
- One line of text, at most one action ("Undo").

## Tooltips

- Supplementary only — nothing essential lives in a tooltip.
- Shows on hover **and** focus, ~150ms delay, hides instantly; never contains buttons or links.

## Tables

- Anatomy: toolbar (search, filters, bulk actions) → sortable header → rows → footer (count + pagination).
- Row states: default / hover (`--fg-soft`) / selected (accent left rule or a subtle accent wash + checkbox) / disabled (muted but still readable).
- Selection: checkbox column; the header checkbox selects the page; a bulk-action bar appears on first selection and names the count ("3 selected").
- An empty table shows the empty state (see `ux-flows.md`) — never naked headers.
- Pagination over infinite scroll whenever position matters ("row 3 of 214"); infinite scroll only for feeds.

## The component state machine (non-negotiable)

Every interactive control defines: `default → hover → focus-visible → active → disabled`, plus `loading` and `error` where it can be submitted. A missing state renders as its nearest neighbor or the browser default — both are regressions.

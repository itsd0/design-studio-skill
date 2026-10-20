# Copy — the words the interface says

Copy is not decoration on top of the layout. It is the part the user actually
reads, and it is where most AI-made interfaces give themselves away: generic
errors, vague buttons, marketing inside the product.

Rules below are checkable. `scripts/score.py` enforces the two marked
**[auto]**.

---

## Errors

Say three things: **what happened**, **why**, and **what to do next**. Name the
object. Never blame the user.

```html
<!-- before -->
<p class="error">Something went wrong. Please try again.</p>

<!-- after -->
<p class="error">The transfer to studio-imac-pro stopped — the peer dropped off
the network. Reconnect it and retry; the partial file is kept.</p>
```

- ❌ "Something went wrong", "An error occurred", "Oops", "Uh oh", "Whoops". **[auto]**
- ❌ Exclamation marks in an error. Never.
- ❌ "Please" unless it is a genuine request ("Please reconnect the peer").
- ✅ State the object: *which* transfer, file, account, run.
- ✅ If the user can fix it, say how. If they cannot, say who can.

## Buttons and links

**Verb + object.** A button says what will happen, not what it is.

```html
<!-- before -->
<button>Submit</button> <button>Continue</button> <button>OK</button>

<!-- after -->
<button>Start transfer</button> <button>Save 3 changes</button>
<button>Delete transfer</button>
```

- ❌ `Submit`, `Send`, `Go`, `Proceed`, `Continue`, `Click here`, `OK`, `Done`. **[auto]**
- ✅ `Send files` (verb + object) is fine; `Send` alone is not.
- ✅ Destructive buttons name the target: `Delete transfer`, never `Delete` alone — unless the surrounding row already names it.
- ✅ One primary action per screen region. Secondary actions read as verbs too.

## Empty states

Distinguish **nothing yet** from **nothing found**. The user's next action is
the point of the screen.

```
Nothing yet          →  No transfers yet. Pair a peer to move your first file.
No results           →  No transfers match "q3". Clear the filter.
Error                →  Transfers could not load. Retry, or check the peer.
```

- ❌ An empty container with no message.
- ❌ `No data` / `Nothing here` with no next action.
- ✅ One sentence, one action, no illustration required.

## Confirmations

Name the consequence and the count. Never "Are you sure?".

```html
<!-- before -->
<p>Are you sure?</p> <button>Yes</button> <button>No</button>

<!-- after -->
<p>Delete 3 transfers from the queue? The files stay on both peers.</p>
<button>Delete 3 transfers</button> <button>Keep them</button>
```

- ✅ The destructive button repeats the target.
- ✅ Say what is *not* affected when that is the real question.
- ✅ Reject stays equally weighted — never a tiny grey "Cancel".

## Onboarding

One idea per step. No marketing inside the product.

- ✅ "Pair a second machine" → the code → "Waiting for the other side…"
- ❌ "Welcome to the future of file transfer!"
- ❌ A tour of five features before the first action.

## Numbers and claims

- Real units, always: `38.4 Gbps`, `4.2 GB`, `1 min ago`.
- Consistent precision in a column. Do not mix `3.1s` and `3.14s`.
- No invented metrics, ever. If you do not have the number, write the sentence
  without it, or label it `[REPLACE · metric]`.
- Comparisons need a basis: "2× faster than the cloud relay **on a local
  network**" — not "2× faster".

## Voice

- Second person, active voice, sentence case.
- Present tense for state ("Sending", not "Will send").
- One name per thing. If it is a *transfer* in the nav, it is not a *job* in the
  table.
- Cut the adverb before the verb: "Save", not "Quickly save".

## The two-minute pass

Before delivery, read every string the user can see out loud:

1. Could a stranger act on it without the screen?
2. Does it name the object?
3. Would a person say it?

If any answer is no, rewrite it. `scripts/score.py` catches the two mechanical
failures (generic errors, vague buttons); the rest is the read-aloud test.

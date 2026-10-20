# The design DNA library

Eighteen reference systems, offline, MIT-licensed, and written for agents. Each
one is a complete, self-consistent set of decisions — tokens, type, spacing,
radius, elevation, component recipes and anti-patterns — that you can bind
verbatim.

They are not brand styles to imitate. They are **starting grammars**: pick one,
bind its tokens, and let the brief decide the content. A library entry that
survives contact with your product is worth more than a hundred swatches.

## How to use one

1. Read the entry (`design-studio library --show <id>`, or the file directly).
2. Copy its `:root` block into the artifact — verbatim, not approximately.
3. Copy its component recipes for the patterns it lists.
4. Keep the anti-patterns. They are the reason the entry works.
5. If your brief does not fit the entry, generate a different direction with
   `python3 scripts/directions.py --brief "…"` rather than bending this one.

## The entries

| id | Use it for | Distance from the default |
|---|---|---|
| `dark-structural-grid` | developer tools, AI infrastructure, agent runtimes, observability | high |
| `light-editorial-serif` | editorial, research, newsletters, long-form products | high |
| `monochrome-operator` | terminals, CLIs, admin consoles, log viewers | very high |
| `warm-human-soft` | health, community, education, consumer onboarding | high |
| `clinical-data` | dashboards of measurements, lab, finance, medical | medium-high |
| `cinematic-ember` | studios, agencies, premium launches, portfolios | high |
| `swiss-poster` | cultural products, conferences, architecture | very high |
| `bauhaus-primary` | education, creative tools, children's products | very high |
| `japanese-minimal` | craft products, ceramics, stationery, slow software | very high |
| `desert-warm` | travel, food, real estate, outdoor | high |
| `noir-luxe` | watches, spirits, private client, jewellery | very high |
| `terminal-green` | security tooling, developer demos | very high |
| `civic-blue` | public services, healthcare portals, utilities | medium |
| `pastel-playful` | consumer apps, kids, learning, community | medium-high |
| `neon-cyber` | games, music tools, events | very high |
| `monochrome-print` | newspapers, archives, documentation | very high |
| `arctic-precision` | instruments, hardware, aerospace, medical devices | high |
| `trading-desk` | trading, monitoring, on-call, logistics | high |

## The rule the library exists to serve

> A skill used by everyone becomes the new default.

Every entry is a *different* grammar on purpose. If your artifact ships with the
same type and palette as everyone else's, the library failed — not the agent. Run
`python3 scripts/score.py index.html` and read the "distance from the default"
line: **2/4 is the floor**, 3/4 is good, 4/4 means you chose deliberately.

## Adding an entry

An entry earns its place when it is (a) a complete system, (b) verifiable with
`python3 scripts/verify.py` and `python3 scripts/score.py`, and (c) a grammar
that is not already covered. Copy the shape of an existing file; keep the
anti-patterns section — that is the part agents skip and reviewers need.

`tests/run_tests.py` (`run_library`) checks every entry: required sections
present, a `:root` block that parses, and the core token pairs passing contrast.

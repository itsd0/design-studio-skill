# Compatibility — what was verified, on what, when

The Agent Skills ecosystem's own audit found that **only 9% of skills are
verified on four or more agents**. "Works everywhere" is usually a claim, not a
finding. This file is the finding: what was actually run, on which agent, and
when.

**Verified on 2026-10-20** on macOS (Darwin), Python 3.14.7, Chrome 141.

## The matrix

| Agent | How it loads design-studio | Verified | Evidence |
|---|---|---|---|
| **OpenCode** | `SKILL.md` + `opencode.json` → MCP | ✅ connected | `opencode mcp list` → `✓ design-studio connected`; the six tools appeared in a live session |
| **Claude Code** | `SKILL.md` + `.claude-plugin/plugin.json` + `.mcp.json` | ✅ resolved | `claude mcp list` → `design-studio: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/mcp_server.py` (pending first-run approval, as Claude Code requires) |
| **Gemini CLI** | `gemini-extension.json` + `.gemini/settings.json` | ✅ connected | `gemini mcp list` → `✓ design-studio … (stdio) - Connected` |
| **Codex CLI** | `SKILL.md` + `.codex-plugin/plugin.json` + `mcp.json` | ✅ registered | `codex mcp add` accepted, `codex mcp get design-studio` → `enabled: true, transport: stdio` (removed after the check to leave the global config as found) |
| **Cursor** | `.cursor-plugin/plugin.json` | ⚠️ manifest only | Cursor was not installed on the verification machine; the manifest validates but was not registered |

## What "verified" means here

Four levels, from weakest to strongest. An entry is only claimed at the level
that was actually run.

| Level | What it proves | Our status |
|---|---|---|
| 1 · Format | `SKILL.md` matches the spec (name, description, budget, sections) | ✅ every platform — `tests/test_skill_md.py` |
| 2 · Tools | The MCP server answers `initialize`, `tools/list`, `tools/call` | ✅ — `tests/run_tests.py` (`run_mcp`) |
| 3 · Registration | The agent accepts and resolves the server | ✅ Claude Code, Codex, Gemini, OpenCode |
| 4 · In-session | An agent invoked a tool and got a real result | ✅ OpenCode (this repository's own session) |

## Reproduce it

```bash
# OpenCode — project-local, relative path
opencode mcp add design-studio -- python3 scripts/mcp_server.py
opencode mcp list

# Claude Code — reads .mcp.json from the project
claude mcp list

# Gemini CLI
gemini mcp add design-studio python3 scripts/mcp_server.py
gemini mcp list

# Codex CLI
codex mcp add design-studio -- python3 scripts/mcp_server.py
codex mcp get design-studio
codex mcp remove design-studio   # if you only wanted to check

# Any MCP client, by hand
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{}}}' \
  | python3 scripts/mcp_server.py
```

All registrations use a **relative** `scripts/mcp_server.py`, because every one
of these agents resolves MCP commands from the project root. Absolute paths
work but break the moment the repository moves.

## What is not verified

- **Cursor** — manifest validated, registration not run (no Cursor on the
  verification machine). Treat it as declared, not verified.
- **Claude.ai / the Claude API** — no filesystem and no shell, so a Python
  toolchain cannot run there. The skill's *rules* work; the gates do not.
- **Windows** — `install.sh` is POSIX. The PowerShell install path is
  documented but the gates were not run on Windows.

## Keeping this honest

Re-run the six commands above before changing this table, and update the date
at the top. A compatibility claim without a date is a guess — the same rule the
independent skill directories apply to their own entries.

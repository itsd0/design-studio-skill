# Adopting Design Studio in your org

## Pinning policy

Float on `main` for evaluation; pin to a release tag in production:

```bash
curl -fsSL https://raw.githubusercontent.com/itsd0/design-studio-skill/main/install.sh | VERSION=v1.5.0 sh
```

Pinned installs verify the tarball against the release's `SHA256SUMS`.
Upgrades are explicit: change `VERSION`, reinstall, restart the agent.
`CHANGELOG.md` lists every breaking-relevant change; the `lint --json`
and `verify --json` contracts (`docs/lint-schema-v1.md`,
`docs/verify-schema-v1.md`) are additive-only.

## Air-gapped and offline use

The skill runs fully offline after install: one `SKILL.md` workflow, local
references and seeds, and a toolchain of standard-library Python scripts. The
render gate and the scorecard need only a Chrome/Chromium binary already on
the machine (without one they report "skipped" and exit 0). The only network
traffic is the install-time HTTPS download from `codeload.github.com` (plus
`github.com` for checksum verification). Mirror the release tarball internally
and point `install.sh` at it, or vendor the directory into your agent image.

The MCP server (`scripts/mcp_server.py`) is local too — it spawns the same
scripts and opens no sockets. The only tool that touches the network is
`scripts/extract.py`, and only when you point it at a URL.

## No telemetry

The project collects nothing: no analytics, no phone-home, no update checks.
Audit surface is small — `find . -type f | wc -l` files, eight Python
scripts, three JavaScript probes, static HTML/CSS otherwise. The render gate
and the scorecard load the artifact in a local headless browser and write
nothing outside the temp directory. The MCP server opens no sockets.

## Trust checklist for security review

- [ ] `SECURITY.md` — supported versions, 90-day patch SLA, private-report channel
- [ ] `SHA256SUMS` per release, verified by the installer
- [ ] CI green on `main` (tests + lint + Pages smoke), branch protection requiring it
- [ ] MIT license, no dependencies in artifacts or tooling

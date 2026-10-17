# Adopting Design Studio in your org

## Pinning policy

Float on `main` for evaluation; pin to a release tag in production:

```bash
curl -fsSL https://raw.githubusercontent.com/itsd0/design-studio-skill/main/install.sh | VERSION=v1.4.0 sh
```

Pinned installs verify the tarball against the release's `SHA256SUMS`.
Upgrades are explicit: change `VERSION`, reinstall, restart the agent.
`CHANGELOG.md` lists every breaking-relevant change; the `lint --json`
contract (`docs/lint-schema-v1.md`) is additive-only.

## Air-gapped and offline use

The skill runs fully offline after install: one `SKILL.md` workflow, local
references and seeds, and a zero-dependency Python linter. The only network
traffic is the install-time HTTPS download from `codeload.github.com` (plus
`github.com` for checksum verification). Mirror the release tarball internally
and point `install.sh` at it, or vendor the directory into your agent image.

## No telemetry

The project collects nothing: no analytics, no phone-home, no update checks.
Audit surface is small — `find . -type f | wc -l` files, one Python script,
static HTML/CSS otherwise.

## Trust checklist for security review

- [ ] `SECURITY.md` — supported versions, 90-day patch SLA, private-report channel
- [ ] `SHA256SUMS` per release, verified by the installer
- [ ] CI green on `main` (tests + lint + Pages smoke), branch protection requiring it
- [ ] MIT license, no dependencies in artifacts or tooling

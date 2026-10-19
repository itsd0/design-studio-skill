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
references and seeds, a zero-dependency Python linter, and a render gate
that needs only a Chrome/Chromium binary already on the machine (without one
it reports "skipped" and exits 0). The only network traffic is the
install-time HTTPS download from `codeload.github.com` (plus `github.com`
for checksum verification). Mirror the release tarball internally and point
`install.sh` at it, or vendor the directory into your agent image.

## No telemetry

The project collects nothing: no analytics, no phone-home, no update checks.
Audit surface is small — `find . -type f | wc -l` files, two Python scripts,
one JavaScript probe, static HTML/CSS otherwise. The render gate loads the
artifact in a local headless browser and writes nothing outside the temp
directory.

## Trust checklist for security review

- [ ] `SECURITY.md` — supported versions, 90-day patch SLA, private-report channel
- [ ] `SHA256SUMS` per release, verified by the installer
- [ ] CI green on `main` (tests + lint + Pages smoke), branch protection requiring it
- [ ] MIT license, no dependencies in artifacts or tooling

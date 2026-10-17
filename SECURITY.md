# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| Latest `v1.x` release | Yes — security fixes within 90 days |
| Older tags | Pin to the latest tag; only the newest release receives fixes |

Always install a pinned, verified release (see `README.md`):

```bash
curl -fsSL https://raw.githubusercontent.com/itsd0/design-studio-skill/main/install.sh | VERSION=v1.4.0 sh
```

Floating `@main` installs receive no integrity guarantee. Releases since v1.4.0
ship a `SHA256SUMS` asset that the installer verifies automatically.

## Reporting a vulnerability

Open a **private** report via the
[GitHub security advisory form](https://github.com/itsd0/design-studio-skill/security/advisories/new).
Do not open a public issue for suspected vulnerabilities.

We aim to acknowledge within 7 days and ship a fix within 90 days.

## Scope notes

- Artifacts the skill generates are plain HTML/CSS/JS with no dependencies and
  no network calls; the skill itself runs fully offline after install.
- The project collects no telemetry. The installer makes one HTTPS download
  from `codeload.github.com` (plus `github.com` for checksum verification).
- Releases are cut from `main` with CI green; per-release `SHA256SUMS`
  provides integrity. Signed git tags are a planned follow-up, not yet in place.

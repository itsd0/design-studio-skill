#!/bin/sh
# Design Studio installer — OpenCode (or any agent with a skills directory).
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/itsd0/design-studio-skill/main/install.sh | sh
#
# Options (environment variables):
#   SKILLS_DIR   target skills directory   (default: ~/.config/opencode/skills)
#   BRANCH       branch to install         (default: main; ignored when VERSION is set)
#   VERSION      release tag to install    (e.g. VERSION=v1.4.0; recommended for teams)
#   CHECKSUMS    verify against SHA256SUMS (default: auto when VERSION is set, never for BRANCH)
#
# Examples:
#   # Pinned, verified (recommended for teams — see SECURITY.md)
#   curl -fsSL https://raw.githubusercontent.com/itsd0/design-studio-skill/main/install.sh | VERSION=v1.4.0 sh
#
#   # OpenCode, floating on main
#   curl -fsSL https://raw.githubusercontent.com/itsd0/design-studio-skill/main/install.sh | sh
#
#   # Claude Code
#   curl -fsSL https://raw.githubusercontent.com/itsd0/design-studio-skill/main/install.sh | SKILLS_DIR=~/.claude/skills sh
set -eu

REPO="itsd0/design-studio-skill"
BRANCH="${BRANCH:-main}"
VERSION="${VERSION:-}"
SKILLS_DIR="${SKILLS_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills}"
DEST="$SKILLS_DIR/design-studio"

say() { printf '%s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

command -v curl >/dev/null 2>&1 || command -v wget >/dev/null 2>&1 || die "needs curl or wget"
command -v tar  >/dev/null 2>&1 || die "needs tar"

TMP="$(mktemp -d "${TMPDIR:-/tmp}/design-studio.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT HUP INT TERM

fetch() { # $1 = url, $2 = output
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$1" -o "$2" || return 1
  else
    wget -qO "$2" "$1" || return 1
  fi
}

if [ -n "$VERSION" ]; then
  case "$VERSION" in v*|*.*) ;; *) die "VERSION must be a release tag like v1.4.0" ;; esac
  URL="https://codeload.github.com/$REPO/tar.gz/$VERSION"
  DIR="design-studio-skill-${VERSION#v}"
  say "downloading $REPO @ $VERSION (pinned)"
  fetch "$URL" "$TMP/skill.tar.gz" || die "download failed — does release '$VERSION' exist?"
  CHECKSUMS="${CHECKSUMS:-auto}"
  if [ "$CHECKSUMS" = "auto" ]; then
    if fetch "https://github.com/$REPO/releases/download/$VERSION/SHA256SUMS" "$TMP/SHA256SUMS" 2>/dev/null; then
      command -v sha256sum >/dev/null 2>&1 || command -v shasum >/dev/null 2>&1 || die "needs sha256sum or shasum to verify"
      ( cd "$TMP" && grep "skill.tar.gz" SHA256SUMS > sums.txt ) || die "SHA256SUMS has no tarball entry"
      if command -v sha256sum >/dev/null 2>&1; then
        ( cd "$TMP" && sha256sum -c sums.txt ) || die "checksum mismatch — do not install"
      else
        ( cd "$TMP" && shasum -a 256 -c sums.txt ) || die "checksum mismatch — do not install"
      fi
      say "checksum verified"
    else
      say "warning: no SHA256SUMS for $VERSION — installing unverified (release predates v1.4.0)"
    fi
  fi
else
  URL="https://codeload.github.com/$REPO/tar.gz/refs/heads/$BRANCH"
  DIR="design-studio-skill-$BRANCH"
  say "downloading $REPO @ $BRANCH (floating — pin VERSION=vX.Y.Z for reproducible installs)"
  fetch "$URL" "$TMP/skill.tar.gz" || die "download failed — is the branch '$BRANCH' right?"
fi

tar -xzf "$TMP/skill.tar.gz" -C "$TMP" || die "extract failed"
SRC="$TMP/$DIR"
[ -f "$SRC/SKILL.md" ] || die "unexpected archive layout — please open an issue"

mkdir -p "$SKILLS_DIR"
if [ -e "$DEST" ]; then
  BAK="$DEST.bak.$(date +%Y%m%d%H%M%S)"
  say "existing install found — moving it to $BAK"
  mv "$DEST" "$BAK"
fi
mv "$SRC" "$DEST"

say ""
say "installed to $DEST"
say "restart your agent to pick up the skill"

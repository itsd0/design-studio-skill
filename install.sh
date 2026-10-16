#!/bin/sh
# Design Studio installer — OpenCode (or any agent with a skills directory).
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/itsd0/design-studio-skill/main/install.sh | sh
#
# Options (environment variables):
#   SKILLS_DIR   target skills directory   (default: ~/.config/opencode/skills)
#   BRANCH       branch to install         (default: main)
#
# Examples:
#   # OpenCode (default)
#   curl -fsSL https://raw.githubusercontent.com/itsd0/design-studio-skill/main/install.sh | sh
#
#   # Claude Code
#   curl -fsSL https://raw.githubusercontent.com/itsd0/design-studio-skill/main/install.sh | SKILLS_DIR=~/.claude/skills sh
set -eu

REPO="itsd0/design-studio-skill"
BRANCH="${BRANCH:-main}"
SKILLS_DIR="${SKILLS_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills}"
DEST="$SKILLS_DIR/design-studio"

say() { printf '%s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

command -v curl >/dev/null 2>&1 || command -v wget >/dev/null 2>&1 || die "needs curl or wget"
command -v tar  >/dev/null 2>&1 || die "needs tar"

TMP="$(mktemp -d "${TMPDIR:-/tmp}/design-studio.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT HUP INT TERM

URL="https://codeload.github.com/$REPO/tar.gz/refs/heads/$BRANCH"

say "downloading $REPO @ $BRANCH"
if command -v curl >/dev/null 2>&1; then
  curl -fsSL "$URL" -o "$TMP/skill.tar.gz" || die "download failed — is the branch '$BRANCH' right?"
else
  wget -qO "$TMP/skill.tar.gz" "$URL" || die "download failed — is the branch '$BRANCH' right?"
fi

tar -xzf "$TMP/skill.tar.gz" -C "$TMP" || die "extract failed"
SRC="$TMP/design-studio-skill-$BRANCH"
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

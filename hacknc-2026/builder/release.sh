#!/usr/bin/env bash
# Publish the release tier (hacknc-2026/release/) to the submission repo.
#
#   builder/release.sh <remote-url-or-name> [branch] [--dry-run]
#   e.g. builder/release.sh git@github.com:<owner>/<project>.git main
#
# Only committed files under release/ are published, with their history. Pushes are
# fast-forward only; nothing is force-pushed.
set -euo pipefail

REMOTE=${1:?usage: builder/release.sh <remote-url-or-name> [branch] [--dry-run]}
BRANCH=main
DRY=""
for arg in "${@:2}"; do
  case "$arg" in
    --dry-run) DRY="--dry-run" ;;
    *) BRANCH="$arg" ;;
  esac
done

cd "$(dirname "$0")/../release"
PREFIX=$(git rev-parse --show-prefix); PREFIX=${PREFIX%/}   # e.g. hacknc-2026/release
cd "$(git rev-parse --show-toplevel)"

fail() { echo "release: $*" >&2; exit 1; }

[ -z "$(git status --porcelain -- "$PREFIX")" ] \
  || fail "uncommitted changes in $PREFIX; commit them first (only committed files ship)"

if git ls-files -- "$PREFIX" | grep -E '(^|/)\.env$|keypair\.json$' >/dev/null; then
  fail "a secret file is tracked under $PREFIX (.env or *keypair.json); remove it from git"
fi

if git grep -n -E '\.\./builder|hacknc-2026/builder' -- "$PREFIX" >/dev/null; then
  git grep -n -E '\.\./builder|hacknc-2026/builder' -- "$PREFIX" >&2
  fail "release files reference builder/; the release tier must stand alone"
fi

SHA=$(git subtree split --prefix="$PREFIX" 2>/dev/null) \
  || fail "git subtree split failed (is $PREFIX committed?)"
echo "release: $PREFIX at $(git log -1 --format=%h "$SHA") -> $REMOTE $BRANCH"
git push $DRY "$REMOTE" "$SHA:refs/heads/$BRANCH"

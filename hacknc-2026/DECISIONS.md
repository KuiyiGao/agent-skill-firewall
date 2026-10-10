# Decisions

One entry per decision: date, decision, why, alternatives considered.

## 2026-10-10: Keep the workspace inside this repo for now
- **Decision:** develop in `hacknc-2026/` on branch `claude/funny-hopper-wbu746` of the
  existing repository until the team creates the submission repo.
- **Why:** the cloud session can only push to this repository; the container is ephemeral,
  so work must be committed and pushed to survive.
- **Later:** move it out with `git subtree split --prefix=hacknc-2026` so the submission
  repo contains only code written during the event.

## 2026-10-10: One Markdown file per API, with YAML frontmatter
- **Decision:** catalog entries are `catalog/<id>.md` with fixed frontmatter fields and fixed
  body sections, validated by `scripts/catalog.py`.
- **Why:** humans and AI builders can read one file per API; the frontmatter is
  machine-filterable (`select`, `index`, `env`); the fixed sections guarantee every entry
  answers the same questions (request structure, sandbox, visualization, scenarios,
  gotchas, mock fallback).
- **Alternatives:** a single big YAML/JSON file (hard to read, merge conflicts between
  parallel writers); free-form notes (not comparable).

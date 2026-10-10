# Decisions

One entry per decision: date, decision, why, alternatives considered.

## 2026-10-10: Keep the workspace inside this repo for now
- **Decision:** develop in `hacknc-2026/` on branch `claude/funny-hopper-wbu746` of the
  existing repository until the team creates the submission repo.
- **Why:** the cloud session can only push to this repository; the container is ephemeral,
  so work must be committed and pushed to survive.
- **Later:** split out only the release tier (see the tiers decision below) so the
  submission repo contains only the shipped project.

## 2026-10-10: Two tiers, release/ and builder/
- **Decision:** `hacknc-2026/release/` holds only what ships (becomes the submission repo
  via `git subtree split --prefix=hacknc-2026/release`); `hacknc-2026/builder/` holds skills,
  progress log, decisions, builder dependencies, `.env` and packaged skills.
- **How agents still find things:** the root `CLAUDE.md` imports `builder/CLAUDE.md`
  (`@builder/CLAUDE.md`, loaded at launch); skills live in `builder/skills/` and are
  symlinked from `.claude/skills/`, which Claude Code follows (docs: skills, "Symlinked
  folders"). A skill placed directly in `builder/.claude/skills/` would only load after
  Claude touches a file in `builder/`, so the symlink is used instead.
- **Rule:** release code never depends on `builder/`; configuration reaches it only through
  environment variables.
- **Deferred:** a unified agent entry document (README-style router for any agent).

## 2026-10-10: One Markdown file per API, with YAML frontmatter
- **Decision:** catalog entries are `catalog/<id>.md` with fixed frontmatter fields and fixed
  body sections, validated by `scripts/catalog.py`.
- **Why:** humans and AI builders can read one file per API; the frontmatter is
  machine-filterable (`select`, `index`, `env`); the fixed sections guarantee every entry
  answers the same questions (request structure, sandbox, visualization, scenarios,
  gotchas, mock fallback).
- **Alternatives:** a single big YAML/JSON file (hard to read, merge conflicts between
  parallel writers); free-form notes (not comparable).

## 2026-10-10: One directory link for skills
- **Decision:** `.claude/skills` is a single symlink to `../builder/skills`, replacing
  per-skill links.
- **Why:** collaborators add a skill by dropping a folder; nothing to register. Verified: a
  fresh Claude Code session in `hacknc-2026/` discovers skills through the directory link.
- **Check:** `python3 builder/skills.py` validates skills and the link (and recreates the
  link if it is missing).

## 2026-10-10: One rules file for Claude Code and Codex
- **Decision:** `builder/AGENT_RULES.md` holds the rules; root `CLAUDE.md` is
  `@builder/AGENT_RULES.md`, root `AGENTS.md` is a symlink to it; skills are linked from both
  `.claude/skills` and `.agents/skills`.
- **Why:** one source of truth for every agent; a neutral file name also avoids Claude Code
  loading a nested `builder/CLAUDE.md` a second time.

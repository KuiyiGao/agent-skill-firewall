# Rules for AI builders (HackNC 2026)

These rules apply to every coding agent working here. Claude Code loads this file through
`CLAUDE.md` (`@builder/AGENT_RULES.md`), Codex through `AGENTS.md` (a link to this file).
Keep one copy of the rules, here. This is the common entry point for every agent.

> Living document: this file and everything it points to are updated continually while the
> builder tooling is under construction. Re-read it at the start of each session and trust
> the latest version over anything you remember.

You are helping a hackathon team build a project at HackNC 2026. The team's direction is
AI-agent monitoring and visualization for finance, or AI agents for a financial company.
The concrete project is not decided yet; check `builder/DECISIONS.md` before assuming one.

## Workspace tiers

Paths below are relative to `hacknc-2026/`.

- `release/` is the shipped project and becomes the submission repo. Put app code, its
  README, its `.env.example` and demo assets there, and nothing else. Release code must not
  import, read or link anything in `builder/`: it has to run after being split out alone,
  and it gets configuration only from environment variables.
- `builder/` is for building: skills, progress log, decisions, builder-tool dependencies,
  real keys in `builder/.env` (git-ignored), packaged skills in `builder/dist/`.
- Skills: drop a folder (or `.skill` file) into `builder/skills/` and run
  `python3 builder/skills.py`. `.claude/skills` (Claude Code) and `.agents/skills` (Codex)
  both link to that folder, so every `ok` skill loads at startup in either agent. Write
  skills in the shared SKILL.md format (`name` + `description` frontmatter) so both can
  use them. Publish `release/` with `builder/release.sh`.

## builder/ is under construction: you may change anything in it

The team is still building the builder tooling, so nothing in `builder/` is frozen. That
includes the skills in `builder/skills/`, `skills.py`, `release.sh`, the API catalog and its
schema, `.env.example`, the READMEs, the PROGRESS/DECISIONS formats, the conventions in
this file, and this file itself. If something there is wrong, missing or in your way,
fix it, extend it or restructure it; you do not need to ask first or keep the current
layout for its own sake.

When you change `builder/`:
- keep it working: run `python3 builder/skills.py` (and the catalog's `validate` if you
  touched the catalog) before committing;
- update the docs that describe what you changed in the same commit;
- add a line to `builder/PROGRESS.md`, and a `builder/DECISIONS.md` entry if you changed a
  convention, so teammates and other agents can follow.

What stays fixed, because it is not builder tooling: the Devpost rules below, secrets never
committed (keys only in `builder/.env`), and `release/` never depending on `builder/`.

## Hard constraints (from the Devpost rules)

- Submission deadline: **Sunday Oct 11, 10:00 AM Eastern**. Demo video max **2 minutes**.
  GitHub link required. One project per team.
- No code written before hacking started may be submitted. Do not copy code from other
  repositories the team owns (including `agent-skill-firewall`); write it fresh in `release/`.
- Judging is a demo fair: 2-minute demo + 2-minute Q&A per judge, Sunday 12:00-1:30 PM.

## Before choosing or calling any external API

Use the `hacknc-api-catalog` skill (`builder/skills/hacknc-api-catalog/`). Its catalog
holds verified request structures, free-tier limits, sandboxes, gotchas and offline mock
designs. Prefer it over memory: several resources changed in 2025-2026 (pricing,
deprecations, SDK breaking changes), and the catalog records what was checked and how.

## Working conventions

- Mock-first: every external call goes through an adapter with a `*_MODE` env switch and a
  fixture-backed offline mode (see the skill's `references/integration-patterns.md`).
- Secrets live in `builder/.env` only. When release code starts reading a variable, add its
  name to `release/.env.example`. Run the app with the keys exported:
  `set -a && . builder/.env && set +a` from `hacknc-2026/`.
- After each work block, append a dated entry to `builder/PROGRESS.md` (what changed, what
  is blocked, next step) and record any non-obvious choice in `builder/DECISIONS.md`.
- If you learn something new about an API (a quota, a broken endpoint, a version), update
  that catalog entry, set `last_checked`, and run
  `python builder/skills/hacknc-api-catalog/scripts/catalog.py validate`.

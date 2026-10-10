# Instructions for AI builders (HackNC 2026)

You are helping a hackathon team build a project at HackNC 2026. The team's direction is
AI-agent monitoring and visualization for finance, or AI agents for a financial company.
The concrete project is not decided yet; check `DECISIONS.md` before assuming one.

## Hard constraints (from the Devpost rules)

- Submission deadline: **Sunday Oct 11, 10:00 AM Eastern**. Demo video max **2 minutes**.
  GitHub link required. One project per team.
- No code written before hacking started may be submitted. Do not copy code from other
  repositories the team owns (including `agent-skill-firewall`); write it fresh here.
- Judging is a demo fair: 2-minute demo + 2-minute Q&A per judge, Sunday 12:00-1:30 PM.

## Before choosing or calling any external API

Use the `hacknc-api-catalog` skill in `.claude/skills/hacknc-api-catalog/`. Its catalog
holds verified request structures, free-tier limits, sandboxes, gotchas and offline mock
designs. Prefer it over memory: several resources changed in 2025-2026 (pricing,
deprecations, SDK breaking changes), and the catalog records what was checked and how.

## Working conventions

- Mock-first: every external call goes through an adapter with a `*_MODE` env switch and a
  fixture-backed offline mode (see the skill's `references/integration-patterns.md`).
- Secrets live in `.env` (git-ignored). Commit `.env.example` only.
- After each work block, append a dated entry to `PROGRESS.md` (what changed, what is
  blocked, next step) and record any non-obvious choice in `DECISIONS.md`.
- If you learn something new about an API (a quota, a broken endpoint, a version), update
  that catalog entry, set `last_checked`, and run `python scripts/catalog.py validate`.

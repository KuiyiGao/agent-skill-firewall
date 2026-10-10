# Progress

Times are Eastern. Newest entries at the top of the log.

## Status board

| Area | State | Owner | Notes |
|---|---|---|---|
| API resource catalog (skill) | done (v1) | AI | 26 entries: 5 tracks-page, 15 resources-doc, 6 finance extras; see `INDEX.md` |
| Project idea | not decided | team | candidate discussed: supervision dashboard for a fictional brokerage's agents |
| Workspace tiers | done | AI | `release/` (ships) + `builder/` (tools); see root `README.md` |
| Unified agent entry | deferred | - | one README-style router for any agent; later |
| Repo for submission | not created | team | split `release/` out with `git subtree split --prefix=hacknc-2026/release` |
| Accounts / keys | not started | team | see `python scripts/catalog.py env` for the variables |
| Demo video | not started | team | due with submission, max 2 min |

## Key times

- Sun Oct 11 10:00 AM: Devpost submission deadline
- Sun Oct 11 12:00-1:30 PM: demo fair (be at the table)
- Sun Oct 11 3:00 PM: closing ceremony, Hamilton Hall 100

## Log

### 2026-10-10 ~12:30
- `builder/CLAUDE.md`: new section saying everything in `builder/` may be changed while the
  tooling is under construction (with the checks to run and what stays fixed).
- Root `AGENTS.md` points non-Claude agents (Codex, Cursor, Gemini CLI) to `builder/CLAUDE.md`.

### 2026-10-10 ~12:20
- Skill drop-in simplified: `.claude/skills` is now one link to `builder/skills/`, so any
  skill folder dropped there loads at startup (verified with a fresh `claude -p` session
  started in `hacknc-2026/`: it listed `hacknc-api-catalog` and a test skill).
- `builder/skills.py`: unpacks dropped `.skill` files (rejects unsafe paths), validates
  SKILL.md frontmatter, checks the link, prints the pip line for skill deps.
- `builder/release.sh`: publishes `release/` to the submission repo with safety checks.
- Skill deps now live per skill (`<skill>/requirements.txt`); `builder/requirements.txt` removed.

### 2026-10-10 ~12:05
- Split the workspace into `release/` (README placeholder, `.gitignore`, `.env.example`)
  and `builder/` (CLAUDE.md, PROGRESS.md, DECISIONS.md, skills, requirements.txt,
  `.env.example` with all 75 catalog variables, dist/).
- Root `CLAUDE.md` imports `builder/CLAUDE.md`; `.claude/skills/hacknc-api-catalog` is a
  symlink to `builder/skills/hacknc-api-catalog` (confirmed: Claude Code discovered it).
- `catalog.py env` now prints each variable once.

### 2026-10-10 ~11:50
- Catalog v1 complete: 26 entries, all pass `catalog.py validate`; `INDEX.md`,
  `catalog.json` and `references/selection-guide.md` written; `SKILL.md` has quick picks.
- Findings that change choices: Snowflake trials may block Cortex `COMPLETE` (MLH's own
  repo); Twilio US SMS on a new trial is effectively blocked (voice calls work); X API is
  pay-per-use since Feb 2026; Yelp Fusion is paid; HERE's no-card plan ended in 2025;
  ArcGIS is the no-card map option; NewsAPI free tier is 24h delayed.
- Open items to verify live once accounts exist: everything marked "(unverified)" that a
  demo depends on (ElevenLabs free credits, Snowflake trial AI functions, faucet limits,
  ArcGIS routing quota).
- Packaged the skill as `builder/dist/hacknc-api-catalog.skill` (git-ignored build output).

### 2026-10-10 ~11:30
- Created this workspace folder (`hacknc-2026/`) on branch `claude/funny-hopper-wbu746`.
- Started the `hacknc-api-catalog` skill: unified entry template, validator/index/select
  script, references for tracks, integration patterns and visualization patterns.
- Research notes: Notion tracks page, Devpost and hacknc.com are not reachable from the
  cloud sandbox; track details come from search snippets (see the skill's
  `references/tracks.md`).

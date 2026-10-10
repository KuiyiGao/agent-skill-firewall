# HackNC 2026 workspace

Our HackNC 2026 project (UNC Chapel Hill, Oct 10-11, 2026), split into two tiers so the
shipped project stays clean.

| Tier | Path | Contents | Ships? |
|---|---|---|---|
| Release | [`release/`](release/) | Only what the Devpost submission repo contains: app code, its README, its `.env.example`, demo assets | yes |
| Builder | [`builder/`](builder/) | What people and AI agents use to build it: skills (API catalog), progress log, decisions, dependencies, `.env` with real keys, packaged skills | no |

```
hacknc-2026/
├── README.md            this map
├── CLAUDE.md            loads builder/CLAUDE.md for AI sessions started here
├── .claude/skills/      symlinks to builder/skills/* so Claude Code finds them at startup
├── release/             → becomes the submission repo
└── builder/
    ├── README.md        builder guide (start here as a human builder)
    ├── CLAUDE.md        rules for AI builders
    ├── PROGRESS.md      status board + dated log
    ├── DECISIONS.md     decisions and why
    ├── skills/          hacknc-api-catalog (and future skills)
    ├── requirements.txt builder-tool dependencies
    ├── .env.example     every API variable from the catalog; copy to .env (git-ignored)
    └── dist/            packaged .skill files (git-ignored)
```

## Rules that keep the tiers separate

- `release/` never imports, reads or links anything in `builder/`; it must work after being
  lifted out on its own. Configuration reaches it only through environment variables.
- Secrets live in `builder/.env` only. `release/.env.example` lists the variable names the
  shipped app needs, with no values.
- Builder-only material (catalog, logs, scratch notes, rehearsal fixtures that are not part
  of the demo) stays out of `release/`.

## Shipping the release tier

```bash
git subtree split --prefix=hacknc-2026/release -b hacknc-release
git push <submission-repo-url> hacknc-release:main
```

## Unified agent entry

Planned: one entry document (README-style) that any agent reads first and that routes it
to the right tier, skill and task. Not implemented yet; until then AI sessions get their
rules from `CLAUDE.md` → `builder/CLAUDE.md`.

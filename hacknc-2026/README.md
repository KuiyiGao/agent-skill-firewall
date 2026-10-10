# HackNC 2026 workspace

Our HackNC 2026 project (UNC Chapel Hill, Oct 10-11, 2026), in two tiers.

| Tier | Path | Contents | Ships? |
|---|---|---|---|
| Release | [`release/`](release/) | What the Devpost submission repo contains: app code, its README, its `.env.example`, demo assets | yes |
| Builder | [`builder/`](builder/) | What people and AI agents use to build it: skills, progress log, decisions, `.env` with real keys, tools | no |

```
hacknc-2026/
├── README.md              this file
├── CLAUDE.md              loads builder/CLAUDE.md for AI sessions started here
├── .claude/skills  ->  builder/skills   (one link; every skill dropped there is loaded)
├── release/               becomes the submission repo; never references builder/
└── builder/
    ├── skills/            drop skills here (folder with SKILL.md, or a .skill file)
    ├── skills.py          check/install skills: python3 builder/skills.py
    ├── release.sh         publish release/ to the submission repo
    ├── CLAUDE.md  PROGRESS.md  DECISIONS.md  README.md
    ├── .env.example       all API variable names; copy to builder/.env (git-ignored)
    └── dist/              packaged .skill files (git-ignored)
```

## Pushing

Day to day, everyone pushes to the shared working branch of this repo. Each person
mostly touches their own folders (`builder/skills/<their-skill>/`, a module in
`release/`), so conflicts stay rare.

```bash
# once
git clone https://github.com/KuiyiGao/agent-skill-firewall && cd agent-skill-firewall
git checkout claude/funny-hopper-wbu746
cd hacknc-2026

# every change
git pull --rebase                       # get teammates' work first
python3 builder/skills.py               # if you added or changed a skill: must say ok
git add release/ builder/               # never add builder/.env (it is git-ignored)
git commit -m "skills: add <name>"      # or "release: <what changed>"
git push                                # if rejected: git pull --rebase, then push again
```

Publishing the release tier to the submission repo (create an empty GitHub repo first):

```bash
builder/release.sh git@github.com:<owner>/<project>.git main --dry-run   # preview
builder/release.sh git@github.com:<owner>/<project>.git main             # publish
```

`release.sh` refuses to run if `release/` has uncommitted changes, tracks a `.env` or
keypair file, or references `builder/`. It publishes only `release/` (with its history)
as the root of the submission repo, fast-forward only. Run it again after every release
change you want judges to see; the last push must happen before Sunday 10:00 AM Eastern.

## Unified agent entry

Planned: one README-style entry that any agent reads first and that routes it to the
right tier, skill and task. Not implemented yet; AI sessions get their rules from
`CLAUDE.md` → `builder/CLAUDE.md`.

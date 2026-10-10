# HackNC 2026 workspace

Our HackNC 2026 project (UNC Chapel Hill, Oct 10-11, 2026), in two tiers.

| Tier | Path | Contents | Ships? |
|---|---|---|---|
| Release | [`release/`](release/) | What the Devpost submission repo contains: app code, its README, its `.env.example`, demo assets | yes |
| Builder | [`builder/`](builder/) | What people and AI agents use to build it: skills, progress log, decisions, `.env` with real keys, tools | no |

```
hacknc-2026/
├── README.md              this file
├── AGENTS.md  ->  builder/AGENT_RULES.md   (Codex reads this)
├── CLAUDE.md              @builder/AGENT_RULES.md (Claude Code reads this)
├── .claude/skills  ->  builder/skills   (Claude Code)
├── .agents/skills  ->  builder/skills   (Codex)
├── release/               becomes the submission repo; never references builder/
└── builder/
    ├── skills/            drop skills here (folder with SKILL.md, or a .skill file)
    ├── skills.py          check/install skills: python3 builder/skills.py
    ├── release.sh         publish release/ to the submission repo
    ├── AGENT_RULES.md     common entry + rules for every agent (living document)
    ├── PROGRESS.md  DECISIONS.md  README.md
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

## Common agent entry

`builder/AGENT_RULES.md` is the one entry point for every building agent. Claude Code
loads it through `CLAUDE.md`, Codex through `AGENTS.md`; both also load every skill in
`builder/skills/` (verified with fresh sessions of each). The file is updated continually.

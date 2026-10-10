# HackNC 2026 workspace

Working folder for our HackNC 2026 project (UNC Chapel Hill, Oct 10-11, 2026).
Everything in here was created during the event.

| Path | What it is |
|---|---|
| `CLAUDE.md` | Instructions for AI builders working in this folder (read first) |
| `PROGRESS.md` | Status board and dated work log; update it after every work block |
| `DECISIONS.md` | Short records of decisions and why |
| `.claude/skills/hacknc-api-catalog/` | Skill: every API / free sandbox from the HackNC pages, in one unified format, plus selection guidance |

## Using the API catalog

```bash
cd .claude/skills/hacknc-api-catalog
pip install pyyaml
python scripts/catalog.py validate                      # schema check
python scripts/catalog.py index                         # rebuild INDEX.md + catalog.json
python scripts/catalog.py select --tag voice --max-risk medium
python scripts/catalog.py select --track mlh-solana
python scripts/catalog.py show elevenlabs
python scripts/catalog.py env elevenlabs alpaca-paper-trading > ../../../.env.example
```

Claude Code picks up the skill automatically when a session is started in this folder
(`.claude/skills/`).

## Moving this folder into its own repo

The Devpost submission needs a GitHub link to the project's code. When the project repo
exists, lift this folder out with its history:

```bash
git subtree split --prefix=hacknc-2026 -b hacknc-2026-only
# then push that branch to the new repo's main
```

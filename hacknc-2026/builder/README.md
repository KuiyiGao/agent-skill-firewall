# Builder tier

Everything used to build the project that does not ship with it. Paths are relative to
`hacknc-2026/`.

| Path | What it is |
|---|---|
| `builder/CLAUDE.md` | Rules for AI builders (loaded automatically via the root `CLAUDE.md`) |
| `builder/PROGRESS.md` | Status board and dated work log; update after every work block |
| `builder/DECISIONS.md` | Short records of decisions and why |
| `builder/skills/hacknc-api-catalog/` | Skill: every API / free sandbox from the HackNC pages in one unified format, plus selection guidance |
| `builder/requirements.txt` | Python dependencies of the builder tools |
| `builder/.env.example` | Every API variable named in the catalog; copy to `builder/.env` and fill in |
| `builder/dist/` | Packaged `.skill` files (git-ignored) |

## Setup

```bash
cd hacknc-2026
python3 -m venv builder/.venv && . builder/.venv/bin/activate
pip install -r builder/requirements.txt
cp builder/.env.example builder/.env          # fill in only the keys you use
```

## Using the API catalog

```bash
CAT=builder/skills/hacknc-api-catalog/scripts/catalog.py
python $CAT validate                          # schema check
python $CAT index                             # rebuild INDEX.md + catalog.json
python $CAT select --tag voice --max-risk medium
python $CAT select --track mlh-solana
python $CAT show elevenlabs
python $CAT env elevenlabs alpaca-paper-trading   # .env lines for chosen APIs
```

Claude Code sessions started in `hacknc-2026/` load the skill at startup through the
symlink `.claude/skills/hacknc-api-catalog`. Symlinks need macOS/Linux, or Windows with
`git config core.symlinks true` and developer mode.

## Adding a skill

```bash
mkdir -p builder/skills/<name>            # SKILL.md + scripts/ + references/
ln -s ../../builder/skills/<name> .claude/skills/<name>
```

Package one for sharing:
`python -m scripts.package_skill <path-to-skill> builder/dist` from the skill-creator skill.

## Running the release app with keys

```bash
set -a && . builder/.env && set +a        # export keys into this shell
# then start the app from release/ as its README says
```

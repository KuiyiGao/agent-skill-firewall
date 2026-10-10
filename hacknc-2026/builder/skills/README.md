# builder/skills: drop your skills here

Every folder in here is a Claude Code skill for everyone on the team. `.claude/skills`
points at this folder, so a session started in `hacknc-2026/` loads all of them at startup.
There is no registration step.

## Add a skill

1. Put it here, as either
   - a folder `builder/skills/<name>/` containing `SKILL.md`, or
   - a packaged `<name>.skill` file (it gets unpacked for you in step 2).
2. Check it from `hacknc-2026/`:
   ```bash
   python3 builder/skills.py
   ```
   `ok` means Claude Code will load it. Fix anything marked `BROKEN`.
3. Commit the folder (see "Pushing" in the workspace README).

## Minimum SKILL.md

```markdown
---
name: my-skill            # lowercase, digits, hyphens; same as the folder name
description: What it does and when Claude should use it. Be specific; this line is how
  Claude decides to load the skill.
---

# My skill

Instructions for Claude. Put long reference material in references/ and scripts in scripts/.
```

## Conventions

- Python dependencies go in `<name>/requirements.txt`; `skills.py` prints one `pip install`
  line for all skills.
- Keys go in `builder/.env`, never inside a skill. Name the env vars in the skill instead.
- Folder names must be unique; restart the Claude Code session after adding a skill.

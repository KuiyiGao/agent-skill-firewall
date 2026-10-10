#!/usr/bin/env python3
"""Check (and install) the builder skills in builder/skills/.

Drop a skill into builder/skills/ in either form, then run this script:
  - a folder containing SKILL.md, or
  - a packaged .skill file (zip); it is unpacked into a folder and the archive moved
    to builder/dist/.

    python3 builder/skills.py          # install packages, validate, show what is usable
    python3 builder/skills.py --force  # also overwrite folders when unpacking packages

Exit code 1 if any skill is broken, or Claude Code / Codex would not see the skills
or the shared rules (builder/AGENT_RULES.md).
Standard library only, so it runs before any setup.
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import zipfile
from pathlib import Path

BUILDER = Path(__file__).resolve().parent
SKILLS = BUILDER / "skills"
DIST = BUILDER / "dist"
WORKSPACE = BUILDER.parent
# Where each agent looks for project skills; each must be a link to builder/skills.
AGENT_LINKS = {
    "Claude Code": WORKSPACE / ".claude" / "skills",
    "Codex": WORKSPACE / ".agents" / "skills",
}
# Where each agent reads project rules; each must resolve to builder/AGENT_RULES.md.
RULES = BUILDER / "AGENT_RULES.md"

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)


def parse_frontmatter(text: str) -> dict | None:
    """Return the YAML frontmatter as a dict (PyYAML if present, else a small parser)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    try:
        import yaml  # optional

        data = yaml.safe_load(m.group(1))
        return data if isinstance(data, dict) else {}
    except ImportError:
        pass
    data: dict = {}
    key = None
    for line in m.group(1).splitlines():
        top = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if top:
            key, value = top.group(1), top.group(2).strip()
            data[key] = "" if value in (">", "|", ">-", "|-") else value.strip("'\"")
        elif key and line.startswith((" ", "\t")):
            data[key] = (data[key] + " " + line.strip()).strip()
    return data


def install_packages(force: bool) -> list[str]:
    """Unpack builder/skills/*.skill archives safely; return messages."""
    msgs = []
    for pkg in sorted(SKILLS.glob("*.skill")):
        try:
            with zipfile.ZipFile(pkg) as z:
                names = [n for n in z.namelist() if not n.endswith("/")]
                tops = {n.split("/", 1)[0] for n in names}
                if len(tops) != 1 or not any(n.endswith("/SKILL.md") for n in names):
                    msgs.append(f"skip {pkg.name}: expected one top folder containing SKILL.md")
                    continue
                top = tops.pop()
                target = SKILLS / top
                if target.exists() and not force:
                    msgs.append(f"skip {pkg.name}: {top}/ already exists (use --force to overwrite)")
                    continue
                for n in names:  # refuse absolute paths and '..' before writing anything
                    dest = (SKILLS / n).resolve()
                    if not str(dest).startswith(str(SKILLS.resolve()) + os.sep):
                        raise ValueError(f"unsafe path in archive: {n}")
                if target.exists():
                    shutil.rmtree(target)
                z.extractall(SKILLS, members=names)
        except (zipfile.BadZipFile, ValueError) as e:
            msgs.append(f"skip {pkg.name}: {e}")
            continue
        DIST.mkdir(exist_ok=True)
        shutil.move(str(pkg), DIST / pkg.name)
        msgs.append(f"installed {pkg.name} -> skills/{top}/ (archive moved to builder/dist/)")
    return msgs


def check_links() -> list[str]:
    """Each agent's skills dir must resolve to builder/skills; recreate missing links."""
    problems = []
    for agent, link in AGENT_LINKS.items():
        if link.exists() and link.resolve() == SKILLS.resolve():
            continue
        if not link.exists() and not link.is_symlink():
            try:
                link.parent.mkdir(exist_ok=True)
                link.symlink_to(Path("..") / "builder" / "skills", target_is_directory=True)
                continue
            except OSError:
                pass
        rel = link.relative_to(WORKSPACE)
        problems.append(
            f"{rel} does not point to builder/skills, so {agent} will not see these skills. "
            f"On Windows enable symlinks (Developer Mode + `git config core.symlinks true`, then "
            f"re-checkout); on macOS/Linux, from hacknc-2026/: rm -rf {rel} && ln -s ../builder/skills {rel}")
    agents_md = WORKSPACE / "AGENTS.md"
    if not (agents_md.exists() and agents_md.resolve() == RULES.resolve()):
        problems.append("AGENTS.md (read by Codex) should be a link to builder/AGENT_RULES.md; "
                        "from hacknc-2026/: rm -f AGENTS.md && ln -s builder/AGENT_RULES.md AGENTS.md")
    claude_md = WORKSPACE / "CLAUDE.md"
    if "@builder/AGENT_RULES.md" not in (claude_md.read_text() if claude_md.is_file() else ""):
        problems.append("CLAUDE.md (read by Claude Code) should contain the line @builder/AGENT_RULES.md")
    return problems


def check_skill(folder: Path) -> tuple[str, list[str], list[str]]:
    """Return (name, errors, warnings) for one skill folder."""
    errors, warnings = [], []
    skill_md = folder / "SKILL.md"
    if not skill_md.is_file():
        return folder.name, ["no SKILL.md in this folder"], []
    meta = parse_frontmatter(skill_md.read_text(encoding="utf-8", errors="replace"))
    if meta is None:
        return folder.name, ["SKILL.md must start with a --- frontmatter block"], []
    name = str(meta.get("name") or "").strip()
    desc = str(meta.get("description") or "").strip()
    if not name:
        errors.append("frontmatter is missing `name`")
    elif not NAME_RE.match(name):
        errors.append(f"name {name!r}: use lowercase letters, digits and hyphens (max 64)")
    elif name != folder.name:
        warnings.append(f"name {name!r} differs from folder {folder.name!r}; rename one to match")
    if not desc:
        errors.append("frontmatter is missing `description` (agents use it to decide when to load the skill)")
    elif len(desc) > 1024:
        warnings.append(f"description is {len(desc)} chars; keep it under 1024")
    elif len(desc) < 40:
        warnings.append("description is very short; say what it does and when to use it")
    return name or folder.name, errors, warnings


def main(argv: list[str]) -> int:
    force = "--force" in argv
    SKILLS.mkdir(exist_ok=True)
    for msg in install_packages(force):
        print(msg)

    link_problems = check_links()
    folders = sorted(p for p in SKILLS.iterdir() if p.is_dir() and not p.name.startswith("."))
    rows, bad, seen = [], 0, {}
    for folder in folders:
        name, errors, warnings = check_skill(folder)
        if name in seen:
            errors.append(f"duplicate name, also used by skills/{seen[name]}/")
        seen.setdefault(name, folder.name)
        deps = (folder / "requirements.txt").is_file()
        status = "BROKEN" if errors else ("ok*" if warnings else "ok")
        bad += bool(errors)
        rows.append((status, folder.name, deps, errors + warnings))

    print(f"\nSkills in builder/skills/ ({len(rows)}):")
    for status, folder, deps, notes in rows:
        print(f"  {status:<7} {folder}{'  [has requirements.txt]' if deps else ''}")
        for n in notes:
            print(f"          - {n}")
    req = [f"builder/skills/{f}/requirements.txt" for _, f, d, _ in rows if d]
    if req:
        print("\nPython deps (run from hacknc-2026/):\n  pip install " + " ".join(f"-r {r}" for r in req))
    for problem in link_problems:
        print(f"\nPROBLEM: {problem}")
    if rows and not link_problems:
        print(f"\n{' and '.join(AGENT_LINKS)} sessions started in hacknc-2026/ load every 'ok' "
              "skill at startup and read builder/AGENT_RULES.md.")
    return 1 if bad or link_problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

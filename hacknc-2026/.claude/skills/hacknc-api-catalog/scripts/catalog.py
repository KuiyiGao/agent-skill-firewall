#!/usr/bin/env python3
"""Validate, index and query the HackNC API catalog.

Each resource is one Markdown file in ../catalog/<id>.md with YAML frontmatter
(the unified fields) and a fixed set of body sections. This script is the only
thing that should parse those files, so the schema lives here.

Usage:
    python scripts/catalog.py validate            # check every entry
    python scripts/catalog.py index               # regenerate INDEX.md + catalog.json
    python scripts/catalog.py select --tag voice --track mlh-elevenlabs --max-risk medium
    python scripts/catalog.py show twilio         # print one entry
    python scripts/catalog.py env elevenlabs solana   # .env.example lines

Requires PyYAML (pip install pyyaml).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

import yaml

SKILL_DIR = Path(__file__).resolve().parent.parent
CATALOG_DIR = SKILL_DIR / "catalog"
INDEX_MD = SKILL_DIR / "INDEX.md"
CATALOG_JSON = SKILL_DIR / "catalog.json"

ENUMS = {
    "category": {
        "llm", "voice", "communication", "news", "social", "local-business", "geo",
        "ml-nlp", "conversational", "dataset", "compute-sim", "blockchain", "database",
        "finance-trading", "finance-data", "synthetic-data", "starter-kit",
    },
    "source": {"resources-doc", "tracks-page", "extra"},
    "status": {"active", "changed", "legacy", "dead", "unknown"},
    "cost_model": {"free", "free-tier", "free-trial", "campus-license", "paid-only", "unknown"},
    "offline_mock": {"easy", "medium", "hard"},
    "risk": {"low", "medium", "high"},
    "verified": {"sdk-source", "official-docs", "search-snippet", "memory"},
}
TRACKS = {
    "hacknc-general", "hacknc-beginner", "hacknc-frutiger-aero", "hacknc-community",
    "hacknc-ig-turing", "mlh-elevenlabs", "mlh-solana", "mlh-gemini", "mlh-tiger-data",
    "mlh-snowflake", "sponsor-finance",
}
REQUIRED_KEYS = [
    "id", "name", "provider", "category", "source", "listed_as", "status", "cost_model",
    "free_allowance", "card_required", "signup_minutes", "auth", "base_url", "env_vars",
    "sdks", "sandbox", "offline_mock", "demo_effect", "integration_hours", "risk",
    "track_fit", "finance_fit", "tags", "verified", "last_checked", "docs",
]
REQUIRED_SECTIONS = [
    "TL;DR", "Request structure", "Simulation & free sandbox", "Visualization ideas",
    "Scenarios (official)", "Finance-agent angle", "Gotchas", "Mock fallback", "Sources",
]
RISK_ORDER = {"low": 0, "medium": 1, "high": 2}
STATUS_PENALTY = {"active": 0, "changed": 0, "legacy": 2, "unknown": 2, "dead": 5}

FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)


def load_entry(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError("missing YAML frontmatter block (--- ... ---)")
    meta = yaml.safe_load(m.group(1)) or {}
    return meta, m.group(2)


def entry_paths() -> list[Path]:
    return sorted(p for p in CATALOG_DIR.glob("*.md") if not p.name.startswith("_"))


def validate_entry(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        meta, body = load_entry(path)
    except (ValueError, yaml.YAMLError) as e:
        return [str(e)]

    for key in REQUIRED_KEYS:
        if key not in meta:
            errors.append(f"missing key: {key}")
    if meta.get("id") != path.stem:
        errors.append(f"id {meta.get('id')!r} != file name {path.stem!r}")
    for key, allowed in ENUMS.items():
        if key in meta and meta[key] not in allowed:
            errors.append(f"{key}={meta[key]!r} not in {sorted(allowed)}")
    for key in ("demo_effect", "finance_fit"):
        v = meta.get(key)
        if not (isinstance(v, int) and 1 <= v <= 5):
            errors.append(f"{key} must be an int 1-5, got {v!r}")
    if not isinstance(meta.get("signup_minutes"), (int, float)):
        errors.append("signup_minutes must be a number")
    if meta.get("card_required") not in (True, False, "unknown"):
        errors.append("card_required must be true | false | unknown")
    for key in ("env_vars", "sdks", "track_fit", "tags", "docs"):
        if key in meta and not isinstance(meta[key], list):
            errors.append(f"{key} must be a list")
    for t in meta.get("track_fit") or []:
        if t not in TRACKS:
            errors.append(f"unknown track id {t!r}")
    if not isinstance(meta.get("last_checked"), (dt.date, str)):
        errors.append("last_checked must be a date YYYY-MM-DD")

    headings = re.findall(r"^## (.+?)\s*$", body, re.M)
    positions = []
    for sec in REQUIRED_SECTIONS:
        if sec not in headings:
            errors.append(f"missing section: ## {sec}")
        else:
            positions.append(headings.index(sec))
    if positions != sorted(positions):
        errors.append("sections out of order (follow _TEMPLATE.md)")
    if re.search(r"(sk-[A-Za-z0-9]{20,}|AC[0-9a-f]{32}|xi-api-key:\s*[0-9a-f]{20,})", body):
        errors.append("looks like a real secret in the body; use env vars")
    return errors


def cmd_validate(_args) -> int:
    bad = 0
    paths = entry_paths()
    for p in paths:
        errs = validate_entry(p)
        if errs:
            bad += 1
            print(f"FAIL {p.name}")
            for e in errs:
                print(f"  - {e}")
    print(f"{len(paths) - bad}/{len(paths)} entries valid")
    return 1 if bad else 0


def all_entries() -> list[dict]:
    out = []
    for p in entry_paths():
        meta, _ = load_entry(p)
        meta["last_checked"] = str(meta.get("last_checked"))
        meta["file"] = f"catalog/{p.name}"
        out.append(meta)
    return out


def score(e: dict) -> int:
    """Rough 'pick me first' score for a finance-agent hackathon build."""
    return (
        2 * e.get("finance_fit", 0)
        + 2 * e.get("demo_effect", 0)
        - 2 * RISK_ORDER.get(e.get("risk"), 2)
        - STATUS_PENALTY.get(e.get("status"), 2)
        + (1 if e.get("offline_mock") == "easy" else 0)
    )


def cmd_index(_args) -> int:
    entries = all_entries()
    CATALOG_JSON.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    order = {"tracks-page": 0, "resources-doc": 1, "extra": 2}
    entries.sort(key=lambda e: (order.get(e["source"], 9), e["category"], e["id"]))
    lines = [
        "# API catalog index",
        "",
        "Generated by `python scripts/catalog.py index`. Do not edit by hand.",
        "",
        "| id | source | category | status | cost | demo | fin | risk | hours | tracks |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for e in entries:
        lines.append(
            f"| [{e['id']}]({e['file']}) | {e['source']} | {e['category']} | {e['status']} | "
            f"{e['cost_model']} | {e['demo_effect']} | {e['finance_fit']} | {e['risk']} | "
            f"{e['integration_hours']} | {', '.join(e.get('track_fit') or [])} |"
        )
    INDEX_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {INDEX_MD.name} and {CATALOG_JSON.name} ({len(entries)} entries)")
    return 0


def cmd_select(args) -> int:
    rows = []
    for e in all_entries():
        if args.tag and not set(args.tag) & set(e.get("tags") or []):
            continue
        if args.track and args.track not in (e.get("track_fit") or []):
            continue
        if args.category and e["category"] != args.category:
            continue
        if args.free and e["cost_model"] not in ("free", "free-tier", "free-trial", "campus-license"):
            continue
        if args.no_card and e.get("card_required") is not False:
            continue
        if RISK_ORDER.get(e["risk"], 2) > RISK_ORDER[args.max_risk]:
            continue
        if e.get("finance_fit", 0) < args.min_finance:
            continue
        if args.offline and e.get("offline_mock") != "easy":
            continue
        if not args.include_dead and e["status"] == "dead":
            continue
        rows.append(e)
    rows.sort(key=score, reverse=True)
    if not rows:
        print("no match; loosen a filter")
        return 1
    for e in rows:
        print(f"{score(e):>3}  {e['id']:<28} {e['category']:<16} risk={e['risk']:<6} "
              f"demo={e['demo_effect']} fin={e['finance_fit']} hours={e['integration_hours']}  {e['file']}")
    return 0


def cmd_env(args) -> int:
    """Print a .env.example block for the chosen entries (default: all non-dead)."""
    wanted = set(args.ids or [])
    for e in all_entries():
        if wanted and e["id"] not in wanted:
            continue
        if not wanted and e["status"] == "dead":
            continue
        if not e.get("env_vars"):
            continue
        print(f"# {e['id']} ({e['auth']})")
        for var in e["env_vars"]:
            print(f"{var}=")
        print()
    return 0


def cmd_show(args) -> int:
    p = CATALOG_DIR / f"{args.id}.md"
    if not p.exists():
        print(f"no entry {args.id}; try: {', '.join(x.stem for x in entry_paths())}")
        return 1
    print(p.read_text(encoding="utf-8"))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate").set_defaults(fn=cmd_validate)
    sub.add_parser("index").set_defaults(fn=cmd_index)
    s = sub.add_parser("select")
    s.add_argument("--tag", action="append", help="match any of these tags (repeatable)")
    s.add_argument("--track", help="prize id, e.g. mlh-solana")
    s.add_argument("--category")
    s.add_argument("--free", action="store_true", help="free, free-tier, free-trial or campus-license only")
    s.add_argument("--no-card", action="store_true", help="exclude anything needing a credit card")
    s.add_argument("--max-risk", choices=list(RISK_ORDER), default="high")
    s.add_argument("--min-finance", type=int, default=1)
    s.add_argument("--offline", action="store_true", help="only entries that are easy to mock offline")
    s.add_argument("--include-dead", action="store_true")
    s.set_defaults(fn=cmd_select)
    sh = sub.add_parser("show")
    sh.add_argument("id")
    sh.set_defaults(fn=cmd_show)
    en = sub.add_parser("env", help="print .env.example lines")
    en.add_argument("ids", nargs="*", help="entry ids (default: all non-dead)")
    en.set_defaults(fn=cmd_env)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())

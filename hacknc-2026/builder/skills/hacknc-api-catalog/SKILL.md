---
name: hacknc-api-catalog
description: Verified catalog of every API and free sandbox listed on the HackNC 2026 Tracks page and Technical Resources doc (Twilio, NewsAPI, Yelp, X/Twitter, Meta/Facebook, Google Maps, HERE, ArcGIS, IBM Watson, Dialogflow, Kaggle, Google research datasets, MATLAB, MLH and IBM starter kits, plus the MLH prize APIs ElevenLabs, Solana, Gemini, Tiger Data, Snowflake) and finance extras (Alpaca paper trading and news, SEC EDGAR, Faker, Claude API). Each entry has the same fields - request structure, free tier, sandbox/simulation, visualization ideas, official scenarios, finance-agent fit, gotchas, offline mock. Use this skill whenever you are choosing, comparing, wiring up or mocking any external API, dataset or sandbox for the HackNC project, deciding which prize track an integration qualifies for, writing an .env.example, or planning what a dashboard can visualize from API data - even if the user just names a service ("add voice alerts", "put it on a map", "log it on-chain") without saying "API".
---

# HackNC API catalog

One Markdown file per resource in `catalog/`, all with the same frontmatter fields and the
same body sections, so you can compare resources and copy working request code without
re-researching. Every claim carries an evidence level, because several of these services
changed a lot between the 2020 resource doc and today (pricing, deprecations, SDK
rewrites), and the research sandbox could not open most vendor docs directly.

## Workflow

1. **Start from the need, not the vendor.** Run a query, or read `INDEX.md` (generated
   table of all entries) and `references/selection-guide.md` (needs → picks, combos):
   ```bash
   cd builder/skills/hacknc-api-catalog        # from hacknc-2026/; .claude/skills/ links here
   python scripts/catalog.py select --tag voice --max-risk medium
   python scripts/catalog.py select --track mlh-solana
   python scripts/catalog.py select --category geo --no-card --offline
   ```
   `select` ranks by a rough score (finance fit and demo effect up; risk, dead/legacy
   status down). Treat it as a shortlist, then read the entries.
2. **Read the whole entry before writing code** (`python scripts/catalog.py show <id>`).
   The Gotchas section is where the hours are saved: stale examples, auth quirks, quotas,
   weekend behavior.
3. **Trust evidence in this order:** `sdk-source` (read from the published SDK package)
   > `official-docs` > `search-snippet` > `memory`. Anything marked "(unverified)" that your
   demo depends on should get one live test early, and the entry updated with the result.
4. **Build the mock first.** Each entry's "Mock fallback" says how to fake it behind the
   same interface. The patterns (mode switches, stub servers, LLM replay, SSE event bus)
   are in `references/integration-patterns.md`. A demo that works with Wi-Fi off is a
   demo that works at the table.
5. **Check prize fit** in `track_fit` against `references/tracks.md` (prize ids, rewards,
   judging format, rules, what is confirmed vs likely).
6. **Visualize deliberately.** Each entry lists ideas; `references/visualization-patterns.md`
   maps data shapes to chart forms and has the Frutiger Aero styling tokens for the theme
   track.
7. **Leave the catalog better.** When you learn something (a limit, a broken endpoint, a
   new SDK version), edit the entry, bump `last_checked`, then run
   `python scripts/catalog.py validate && python scripts/catalog.py index`.

## Quick picks (details and reasons in `references/selection-guide.md`)

- **Use first:** `claude-api` (agent brain), `alpaca-paper-trading` + `alpaca-news`
  (orders and finance news, one free key), `faker` (safe PII), `elevenlabs` (voice alerts
  and voice approval), `solana` (tamper-evident audit on devnet), `arcgis-location-platform`
  (no-card maps), `tiger-data` (time-series events), `sec-edgar` (filings).
- **Use with care:** `twilio` (voice calls work on trial, SMS mostly does not),
  `google-maps-platform` (needs a card), `gemini-api` (give it a real decision to win
  `mlh-gemini`), `snowflake` (trial may block Cortex `COMPLETE`; test first),
  `kaggle-datasets` (download before venue Wi-Fi), `meta-graph-api` (WhatsApp test number).
- **Skip unless a sponsor changes the picture:** `x-api`, `yelp`, `here-platform`,
  `dialogflow`, `ibm-watson` as a main model, `ibm-call-for-code-starter-kits`,
  `capital-one-nessie`.

## Unified fields

| Field | Meaning |
|---|---|
| `id` | kebab-case, equals the file name |
| `name`, `provider` | what and who |
| `category` | enum, see below |
| `source` | `tracks-page`, `resources-doc` (the two HackNC pages) or `extra` (added for the finance direction) |
| `listed_as` | the exact label on the HackNC page ("" for extras) |
| `status` | `active`, `changed` (works but differs from the 2020 doc), `legacy` (archived/stale), `dead`, `unknown` |
| `cost_model` | `free`, `free-tier`, `free-trial`, `campus-license`, `paid-only`, `unknown` |
| `free_allowance` | concrete numbers for what is free |
| `card_required` | credit card needed to get going |
| `signup_minutes` | realistic minutes from zero to a working key |
| `auth`, `base_url`, `env_vars` | how to authenticate, where to call, which env vars our code reads |
| `sdks` | pinned package versions that were checked |
| `sandbox` | the free simulation mode (test credentials, devnet, paper trading, trial) or "none" |
| `offline_mock` | `easy` / `medium` / `hard` to fake locally |
| `demo_effect` | 1-5, how much it shows in a 2-minute demo |
| `integration_hours` | one person, including signup |
| `risk` | `low` / `medium` / `high`: signup friction, quotas, flakiness, review gates |
| `track_fit` | prize ids (see `references/tracks.md`) |
| `finance_fit` | 1-5, usefulness for finance-agent monitoring or financial-company agents |
| `tags` | free-form capability tags used by `select --tag` |
| `verified`, `last_checked`, `docs` | weakest evidence behind key claims, date, primary links |

Body sections, always in this order: **TL;DR · Request structure · Simulation & free
sandbox · Visualization ideas · Scenarios (official) · Finance-agent angle · Gotchas · Mock
fallback · Sources**. The template with guidance per section is `catalog/_TEMPLATE.md`.

Categories: `llm`, `voice`, `communication`, `news`, `social`, `local-business`, `geo`,
`ml-nlp`, `conversational`, `dataset`, `compute-sim`, `blockchain`, `database`,
`finance-trading`, `finance-data`, `synthetic-data`, `starter-kit`.

## Scoring rubric (keep new entries consistent)

- `demo_effect`: 5 = judges see or hear something memorable in seconds (voice, live map,
  on-chain proof); 3 = visible but ordinary (a table, a chart); 1 = plumbing nobody sees.
- `finance_fit`: 5 = core to agents acting on money/clients (orders, client data, market
  news); 3 = useful supporting signal; 1 = no sensible finance use.
- `risk`: high if a key needs review/approval, a card, days of verification, or the free
  tier is too small for rehearsals; medium if quotas or setup can bite; low otherwise.

## Files

- `INDEX.md`, `catalog.json`: generated summary (do not hand-edit).
- `catalog/<id>.md`: the entries; `catalog/_TEMPLATE.md`: the schema with guidance.
- `references/selection-guide.md`: needs → picks, recommended combos, what to skip.
- `references/tracks.md`: prizes, judging, rules, and the verbatim resource-doc structure.
- `references/integration-patterns.md`: mock-first adapters, replay, secrets, SSE.
- `references/visualization-patterns.md`: data shape → chart form, status colors, Aero CSS.
- `scripts/catalog.py`: `validate`, `index`, `select`, `show`, `env`.

## Adding an entry

Copy `catalog/_TEMPLATE.md` to `catalog/<id>.md`, fill every field and section (write
"none" or "weak fit, because ..." rather than leaving gaps), cite sources with their
evidence level, then validate and re-index. Never paste real keys; use the env var names.

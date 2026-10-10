---
# ---- identity -------------------------------------------------------------
id: mlh-starter-kits
name: MLH Hackathon Starter Kits & Guides
provider: Major League Hacking (MLH)
category: starter-kit
source: resources-doc
listed_as: "Hackathon Starter Kits & Guides"
# ---- availability ---------------------------------------------------------
status: changed
cost_model: free
free_allowance: "Guides/boilerplates free; sponsor perks per MLH pages: $50 MongoDB Atlas credits, 120-day student Snowflake trial (search-snippet); no Gemini credits from MLH"
card_required: false
signup_minutes: 5
auth: "none for the guides; each sponsor kit needs that sponsor's own key"
base_url: "https://hack.mlh.io/learn (MLH content now also served at https://www.mlh.com/resources/learn)"
env_vars: [DATABASE_URL, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET]
sdks: ["git: github.com/MLH/mlh-hackathon-flask-starter (archived 2022)", "git: github.com/MLH/mlh-hackathon-nodejs-starter (archived 2022)"]
# ---- simulation -----------------------------------------------------------
sandbox: "Kits run on localhost; sponsor sandboxes: Solana devnet + faucet, Snowflake trial (Cortex COMPLETE blocked on trials)"
offline_mock: easy
# ---- fit for builders -----------------------------------------------------
demo_effect: 1
integration_hours: "0.5-2"
risk: medium
track_fit: [hacknc-beginner, mlh-gemini, mlh-elevenlabs, mlh-solana, mlh-snowflake]
finance_fit: 1
tags: [starter-kit, boilerplate, mlh, onboarding, prize-rules]
# ---- provenance -----------------------------------------------------------
verified: search-snippet
last_checked: 2026-10-10
docs: ["https://hack.mlh.io/learn", "https://www.mlh.com/resources/learn", "https://www.mlh.com/resources/software", "https://github.com/MLH", "https://github.com/MLH/mlh-hack-days-organizer-guide"]
---

## TL;DR
This isn't an API. It's MLH's page of guides plus sponsor "starter kits". In 2026 MLH content is served at mlh.com: event pages exist at both `hack.mlh.io/<event>` and `mlh.com/events/<event>`. According to search snippets, the Learn page lists partner kits such as a **MongoDB Starter Kit** and an **Auth0 Starter Kit**, and sponsor quickstarts sit behind `mlh.link/...` short links. MLH's own Flask and Node.js boilerplates have been **archived since early 2022**. The real value for us is the quickest valid integration for each MLH prize, and knowing what the judges will check.

## Request structure
**How to use a kit.** The generic loop is clone, env, run:
```bash
git clone --depth 1 https://github.com/MLH/mlh-hackathon-flask-starter app && cd app
cp .env.example .env        # DATABASE_URL, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
flask run                   # http://localhost:5000; GitHub OAuth callback /auth/callback/github
# Node variant: MLH/mlh-hackathon-nodejs-starter -> npm install && npm start (needs Postgres)
```

**Sponsor quickstarts by MLH track.** Evidence rules come from MLH's Hack Days organizer guide (reviewed August 2026). We assume full hackathons apply the same rules (inferred).
| track | starter resource | what judges must see |
|---|---|---|
| mlh-gemini | `mlh.link/gemini-quickstart`, Google AI Studio, Gemini API docs. MLH **cannot provide Gemini credits** | Gemini API actually used in the app (code, README, or demo) |
| mlh-snowflake | `mlh.link/snowflake-demo` (Python project using Snowflake packages + API), `mlh.link/snowflake-tutorial` (REST example), 120-day student trial (search-snippet) | Snowflake's AI capabilities actually used |
| mlh-solana | `mlh.link/solana`, `/solana-docs`, `/solana-tutorials`, `/solana-templates`; devnet faucet; one-command Rust + Solana CLI + Anchor setup (search-snippet) | integration named in README; show code, a tx, or a deployed program |
| mlh-elevenlabs | `mlh.link/elevenlabs` (search-snippet) | (unverified) |
| mlh-tiger-data | no MLH kit found (unverified) | (unverified) |
| MongoDB / Auth0 | Learn page kits; Auth0 login "in about ten minutes" (search-snippet) | n/a |

## Simulation & free sandbox
The boilerplates run fully on localhost. **Solana:** use devnet with the faucet, so no real money is involved. **Snowflake:** MLH's own `snowflake-postcard` README (May 2026) warns that `SNOWFLAKE.CORTEX.COMPLETE` fails on trial accounts with `AI function COMPLETE is not available for trial accounts`. Check whether the 120-day student trial avoids this before you build an LLM feature on it (unverified). **Gemini:** use the AI Studio free tier.

## Visualization ideas
The kits aren't data sources, so these are about making the integration visible in a 2-minute demo:
- A **"Powered by" status panel**: one tile per sponsor API showing last call, latency, and OK/error. It doubles as agent-monitoring UI.
- An **architecture strip** in the demo video that highlights each sponsor call, which helps the judges' evidence check.
- A **README "Prize evidence" table**: track, file:line, and a screenshot of the call.

## Scenarios (official)
- **Gemini:** a chatbot giving personalized advice, summarizing complex research papers, generating code, scripts, or music.
- **Snowflake:** a RAG chatbot over your data; AI summarization, generation, or extraction; a data app without stitching separate AI services together.
- **Solana:** apps that use onchain state, ownership, or transactions; payments or finance experiences; a web or mobile app with Solana as the backend.
- **Flask/Node starters:** API calls, OAuth login, and database setup (GitHub blog on the MLH starters).

## Finance-agent angle
The direct fit is weak: the kits contain no finance content. The indirect value is real, because kits are how you stack MLH prizes onto a finance-agent build:
- Gemini as the agent LLM (mlh-gemini).
- Snowflake Cortex for RAG over filings or transactions (mlh-snowflake, if trial limits allow).
- A Solana devnet ledger as a tamper-evident audit trail of agent actions (mlh-solana).
- ElevenLabs voice alerts when the monitor flags something (mlh-elevenlabs).

## Gotchas
- hack.mlh.io and mlh.com are unreachable from our sandbox, so the list of kits comes from search snippets. Open the page in a browser at the venue and update this entry.
- The archived boilerplates pin 2019-2021 dependencies. Other MLH starters (Snap Kit, Transposit, Blockstack, UiPath) target dead or changed products. Use them for structure only.
- Devpost rule: no pre-written code. Cloning a public starter is normally allowed, but say so in the README (inferred). Never copy the team's own older repos (see CLAUDE.md).
- MLH's contest terms on GitHub still show the July 1, 2025 to June 30, 2026 season. Prize hardware and categories vary by event and quarter, so trust the HackNC prize page.
- MLH can't hand out Gemini credits. Budget for free-tier rate limits.

## Mock fallback
A kit is just code, so vendor it (clone at home, commit only what you use). For each sponsor call, keep a `<SPONSOR>_MODE=fixture|live` switch that returns canned JSON. The demo then survives bad Wi-Fi while the README still points to the live code path for the judges.

## Sources
- https://raw.githubusercontent.com/MLH/mlh-hack-days-organizer-guide/main/{SUMMARY.md,partner-details/partner-details/google-gemini.md,snowflake.md,solana.md} (official-docs, "Last reviewed: August 2026")
- https://raw.githubusercontent.com/MLH/snowflake-postcard/main/README.md (Cortex trial limitation) (official-docs)
- https://raw.githubusercontent.com/MLH/mlh-hackathon-flask-starter/master/README.md and the nodejs-starter README (official-docs)
- GitHub search org:MLH (archived flags, push dates) (official-docs)
- https://raw.githubusercontent.com/MLH/mlh-policies/main/contest-terms.md (official-docs)
- Web search: mlh.com/resources/learn (MongoDB/Auth0 kits), mlh.com/resources/software, mlh.link quickstarts, prize pages (search-snippet)

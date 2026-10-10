# Selection guide

How to choose from the catalog quickly. Verdicts summarize each entry as of 2026-10-10;
read the entry before building on it. "Finance" means AI-agent monitoring/visualization
for finance, or AI agents for a financial company.

## Contents
1. Verdict per resource
2. Need → pick
3. Minimum meaningful use per MLH prize
4. Things with lead time (do these first)
5. Skip list
6. Example stacks

## 1. Verdict per resource

**From the Tracks page (MLH prize APIs)**

| id | Verdict |
|---|---|
| `elevenlabs` | **Use.** TTS alert in 1-2h; voice agent with client tools (approve/reject) in 3-5h is the prize-worthy use. No card. |
| `solana` | **Use** for tamper-evident audit: anchor hash-chain head via Memo on devnet, verify page, live tamper test. 1-2h. Fund the keypair early. |
| `gemini-api` | **Optional.** Free key in minutes, no card. Earn the prize with a real decision role (second-opinion risk check, reading a statement PDF/chart image), not decoration. |
| `tiger-data` | **Use if you have time-series** (agent events, ticks). Free service, no card, plain Postgres; hypertables + continuous aggregates drive live charts. Local Docker fallback. |
| `snowflake` | **Risky.** No-card trial, but MLH's own repo says Cortex `COMPLETE` is blocked on trials and the prize wants "AI capabilities actually used". Test `AI_COMPLETE` in the first 10 minutes or skip. |

**From the Technical Resources doc**

| id | Verdict |
|---|---|
| `twilio` | **Voice only.** Keypad approval call to a verified phone works on trial (needs a public URL). US SMS on a new trial is effectively blocked; use Console Virtual Phone for on-screen SMS. |
| `newsapi` | **Skip for finance.** 24h delay, 100 req/day, localhost-only CORS; use `alpaca-news`. Fine for general-news side features. |
| `yelp` | **Skip.** Fusion became the paid Places API; only a 30-day, 5,000-call evaluation trial. |
| `x-api` | **Skip.** Pay-per-use since Feb 2026, card required, auto-paging burns credits. |
| `meta-graph-api` | **Niche.** WhatsApp Cloud API test number is free (up to 5 verified phones): a usable alert channel. Page/Insights work needs app roles or review. |
| `google-maps-platform` | **Best-looking map, card required.** Per-SKU free caps are plenty; Places (New) needs field masks; HeatmapLayer removed (use deck.gl). |
| `arcgis-location-platform` | **Default map choice.** No card, 2M tiles + 20k geocodes/month, 3D globe fits Frutiger Aero. New keys are expiring "API key credentials". |
| `here-platform` | **Skip.** No-card plan ended 2025; card needed; weakest fit. |
| `ibm-watson` | **Guardrail only.** watsonx.ai Granite Guardian / PII detection as a second-vendor check; card needed; not the main model. |
| `dialogflow` | **Skip** unless you want a fixed-flow front door for banking intents; CX needs billing. |
| `kaggle-datasets` | **Use for offline data** (fraud/transactions/news sentiment). New `KAGGLE_API_TOKEN` auth; download before the venue Wi-Fi. |
| `google-research-datasets` | **Weak, one gem:** Schema-Guided Dialogue has bank/payment dialogues with recorded `TransferMoney`/`CheckBalance` calls, i.e. ready-made agent traces for a monitor demo. |
| `matlab` | **Only if a teammate knows it.** Free event licenses with all toolboxes (Financial, Risk, Econometrics, Simulink); official MATLAB MCP server; not a web API. |
| `mlh-starter-kits` | **Reference.** MLH's GitHub starters are archived (2022); useful for the per-prize "what judges must see" table and mlh.link quickstarts. |
| `ibm-call-for-code-starter-kits` | **Skip.** Archived 2020 kits on retired Watson services and Cloud Foundry. |

**Extras (not on the HackNC pages, added for finance)**

| id | Verdict |
|---|---|
| `claude-api` | **Agent brain.** Tool runner + approval gate inside tool functions. Paid. Replay mode for demos. |
| `alpaca-paper-trading` | **Use.** Email-only paper account, $100k simulated; weekend orders queue as `accepted`. Mock via `url_override`. |
| `alpaca-news` | **Use.** Ticker-tagged finance news with full content, same keys. Cache it. |
| `sec-edgar` | **Use for grounding.** Free filings/XBRL facts, no key, User-Agent required, backend only. |
| `faker` | **Use.** Seeded synthetic clients with PII; the safe way to demo PII-leak blocking. |
| `capital-one-nessie` | **Dead.** Reported down since 2025; replicate its shapes locally if a Capital One prize appears. |

## 2. Need → pick

| Need | First pick | Backup | Avoid |
|---|---|---|---|
| Agent LLM with tools | `claude-api` | `gemini-api` | Dialogflow or Watson as the main brain |
| Second-opinion / guardrail model | `gemini-api` | `ibm-watson` (Granite Guardian) | - |
| Human approval by voice | `elevenlabs` (voice agent, client tools) | `twilio` keypad call | SMS on a trial |
| Alert to a phone | `twilio` voice call | `meta-graph-api` WhatsApp test number | `twilio` SMS, `x-api` |
| Market news | `alpaca-news` | `newsapi` (24h late) | `x-api` (paid) |
| Orders / portfolio | `alpaca-paper-trading` | local stub server | `capital-one-nessie` |
| Client records with PII | `faker` | - | any real data |
| Filings / fundamentals | `sec-edgar` | `snowflake` Marketplace data | - |
| Time-series store + live aggregates | `tiger-data` | local TimescaleDB Docker | - |
| Warehouse + SQL LLM functions | `snowflake` (test the trial first) | DuckDB mock | - |
| Tamper-evident audit | `solana` | local hash chain only | custom on-chain programs (time) |
| Map / location story | `arcgis-location-platform` | `google-maps-platform` (card) | `here-platform` |
| Offline datasets | `kaggle-datasets` | `google-research-datasets` (SGD traces) | - |
| Quant / simulation math | `matlab` (if known) | Python (numpy/pandas) | - |

Run `python scripts/catalog.py select ...` to re-rank after you edit entries.

## 3. Minimum meaningful use per MLH prize

MLH judges look for the sponsor tech actually doing work in the app (shown in code,
README or demo). A logo or a one-line call rarely wins.

| Prize | Minimum that reads as "meaningful" | Hours |
|---|---|---|
| `mlh-elevenlabs` | A voice agent that queries app state and takes an action through client tools (e.g. "what's pending?" → "approve it"), with TTS alerts as fallback | 3-5 |
| `mlh-solana` | On-chain anchors + a verify view anyone can run + a live tamper demo; explorer links in the README | 1-2 |
| `mlh-gemini` | Gemini makes a decision that changes app behavior (risk second opinion, document/chart extraction feeding the pipeline) | 1-2 |
| `mlh-tiger-data` | Hypertables + continuous aggregates powering a live chart; show a query that would be slow without them | 1-3 |
| `mlh-snowflake` | Cortex AI functions over data stored in Snowflake (only if the trial allows), e.g. batch-classifying events, plus a Streamlit view | 2-4 |

Pick two or three; each prize you chase costs integration time and demo seconds.

## 4. Things with lead time (do these first)

- Solana: create the keypair and fund 2-5 devnet SOL from several teammates (faucets rate-limit).
- Twilio: verify the supervisor's phone number; get a trial number; set up a public URL (cloudflared/ngrok) for `<Gather>` callbacks.
- Snowflake: start the trial on the day, create a PAT + network policy, run `AI_COMPLETE` once.
- Google Maps: billing account with a card; restrict the key to your origins.
- ArcGIS: create an API key credential and note its expiry date.
- ElevenLabs: create the agent and declare client tools in the dashboard; ask the MLH desk for credits.
- Kaggle: download datasets before you are on venue Wi-Fi.
- Alpaca: paper keys; cache a week of news; cache Friday closing prices.

## 5. Skip list (and why)

`x-api` (paid), `yelp` (paid after a short trial), `here-platform` (card, weak fit),
`ibm-call-for-code-starter-kits` (archived, retired services), `capital-one-nessie` (down),
`dialogflow` (billing, superseded by LLM agents for this use). Revisit only if a sponsor at
the event offers credits or a prize for one of them.

## 6. Example stacks

These are options, not decisions; see `DECISIONS.md` in the workspace for what the team chose.

- **Agent supervision dashboard (finance):** `claude-api` + `alpaca-paper-trading` +
  `alpaca-news` + `faker` + `elevenlabs` + `solana` (+ `tiger-data` as the event store).
  Prizes: general, frutiger-aero (styling), mlh-elevenlabs, mlh-solana (+ mlh-tiger-data).
- **Financial-firm assistant with guardrails:** `claude-api` + `sec-edgar` + `alpaca-news`
  + `gemini-api` (second opinion) + `elevenlabs` (voice) + `faker`.
  Prizes: general, mlh-gemini, mlh-elevenlabs.
- **Fraud / transaction monitoring map:** `kaggle-datasets` (PaySim, card fraud) +
  `tiger-data` + `arcgis-location-platform` + `twilio` voice alerts.
  Prizes: general, mlh-tiger-data, frutiger-aero (3D ocean globe).

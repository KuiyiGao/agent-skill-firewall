---
# ---- identity -------------------------------------------------------------
id: snowflake
name: Snowflake (Cortex AI + SQL API)
provider: Snowflake Inc.
category: database
source: tracks-page
listed_as: "[MLH] Best Use of Snowflake API"
# ---- availability ---------------------------------------------------------
status: active
cost_model: free-trial
free_allowance: "30-day trial with $400 of usage, no billing info, ends at whichever runs out first (official FAQ snippet). MLH advertises a 120-day student trial via mlh.link/snowflake-signup (unverified for Oct 2026). No permanent free tier"
card_required: false
signup_minutes: 15
auth: "REST (SQL API, Cortex): Authorization: Bearer <PAT> + X-Snowflake-Authorization-Token-Type: PROGRAMMATIC_ACCESS_TOKEN. Python: authenticator=PROGRAMMATIC_ACCESS_TOKEN, token=<PAT> (or key-pair JWT)"
base_url: "https://<orgname>-<account_name>.snowflakecomputing.com/api/v2"
env_vars: [SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PAT, SNOWFLAKE_PASSWORD, SNOWFLAKE_WAREHOUSE, SNOWFLAKE_MODE]
sdks: ["python: snowflake-connector-python==4.8.0", "python: snowflake-snowpark-python==1.55.1", "python: snowflake-core==1.13.2", "python: snowflake-ml-python==2.4.0 (snowflake.cortex.* deprecated)", "cli: snowflake-cli==3.29.0", "python: streamlit==1.65.0"]
# ---- simulation -----------------------------------------------------------
sandbox: "Trial credits are a real account (no card); Snowpark local_testing session for DataFrame code; free Marketplace datasets"
offline_mock: medium
# ---- fit for builders -----------------------------------------------------
demo_effect: 4
integration_hours: "2-4"
risk: medium
track_fit: [mlh-snowflake, hacknc-general, sponsor-finance]
finance_fit: 4
tags: [llm, cortex, sql, data-warehouse, rest-api, streamlit, marketplace, finance-data, agents, pat]
# ---- provenance -----------------------------------------------------------
verified: search-snippet
last_checked: 2026-10-10
docs: ["https://docs.snowflake.com/en/user-guide/snowflake-cortex/aisql", "https://docs.snowflake.com/en/developer-guide/sql-api/submitting-requests", "https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-rest-api", "https://docs.snowflake.com/en/user-guide/programmatic-access-tokens", "https://www.mlh.com/partners/snowflake"]
---

## TL;DR
Snowflake is a cloud data warehouse. Its **Cortex AI** features expose hosted LLMs in two ways: as SQL functions (`AI_COMPLETE`, `AI_CLASSIFY`, `AI_SENTIMENT` and others) and as REST endpoints. That is the MLH pitch: many LLMs on one account. The trial gives $400 or 30 days with no card. Budget about 15 minutes before your first API call, because a new account needs a **PAT**, a **network policy** for that PAT, a warehouse, and usually cross-region inference turned on.

## Request structure
One-time setup in a Snowsight worksheet as ACCOUNTADMIN. This is the throwaway-trial version, never for production:
```sql
ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';   -- needed for Claude/GPT-class models in most regions
CREATE WAREHOUSE IF NOT EXISTS HACK_WH WAREHOUSE_SIZE = XSMALL AUTO_SUSPEND = 60 AUTO_RESUME = TRUE INITIALLY_SUSPENDED = TRUE;
CREATE NETWORK POLICY IF NOT EXISTS hack_np ALLOWED_IP_LIST = ('0.0.0.0/0');   -- PATs require a network policy by default
ALTER USER <you> SET NETWORK_POLICY = hack_np;
ALTER USER <you> ADD PROGRAMMATIC ACCESS TOKEN hacknc_pat ROLE_RESTRICTION = 'ACCOUNTADMIN' DAYS_TO_EXPIRY = 7;
-- token_secret is shown ONCE -> .env SNOWFLAKE_PAT ; SNOWFLAKE_ACCOUNT = orgname-account_name (hyphen)
```
**SQL API** (`POST /api/v2/statements`). The body fields are `statement`, `timeout` (s), `warehouse`, `role`, `database`, `schema`, `bindings`, and `parameters`:
```bash
curl -s -X POST "https://${SNOWFLAKE_ACCOUNT}.snowflakecomputing.com/api/v2/statements" \
  -H "Authorization: Bearer ${SNOWFLAKE_PAT}" \
  -H "X-Snowflake-Authorization-Token-Type: PROGRAMMATIC_ACCESS_TOKEN" \
  -H "Content-Type: application/json" -H "Accept: application/json" \
  -d "{\"statement\":\"SELECT AI_CLASSIFY('agent trader-1: BUY 50000 GME at market', ['PASS','HOLD','BLOCK']) AS v\",
       \"timeout\":60,\"warehouse\":\"${SNOWFLAKE_WAREHOUSE}\",\"role\":\"ACCOUNTADMIN\"}"
# 200 -> {"resultSetMetaData":{"numRows":1,"rowType":[{"name":"V","type":"object",...}]},
#         "data":[["{\"labels\":[\"BLOCK\"]}"]],"code":"090001","statementHandle":"01b...",
#         "message":"Statement executed successfully."}   (field list partly unverified)
# 202 -> still running: poll GET /api/v2/statements/{statementHandle}
```
**Cortex REST** uses the same host and headers. The paths below come from snowflake-core 1.13.2 unless marked otherwise:
- `POST /api/v2/cortex/inference:complete` takes `{"model","messages":[{"role","content"}],"max_tokens","temperature","response_format","tools","stream"}`. **`stream` defaults to true (SSE)**, so send `"stream": false` to get JSON back as `choices[0].message.content`.
- `POST /api/v2/cortex/v1/chat/completions` is OpenAI-compatible. It is what a Sept 2026 MLH-track project used (sdk-source, third-party). `GET /api/v2/cortex/models` lists the models you can call.
- `POST /api/v2/cortex/agent:run` defines the agent inline. `POST /api/v2/databases/{db}/schemas/{s}/agents/{name}:run` runs an agent object, which supports multiple tools and returns SSE unless `stream:false` (search-snippet).
- `POST /api/v2/cortex/analyst/message` turns natural language into SQL over a semantic model or semantic view (search-snippet). `POST /api/v2/databases/{db}/schemas/{s}/cortex-search-services/{name}:query` runs RAG retrieval.

Python. The `paramstyle="qmark"` setting keeps the SQL identical to the DuckDB mock below:
```python
import json, os, snowflake.connector
conn = snowflake.connector.connect(
    account=os.environ["SNOWFLAKE_ACCOUNT"], user=os.environ["SNOWFLAKE_USER"],
    authenticator="PROGRAMMATIC_ACCESS_TOKEN", token=os.environ["SNOWFLAKE_PAT"],  # or password=os.environ["SNOWFLAKE_PASSWORD"]
    warehouse=os.environ["SNOWFLAKE_WAREHOUSE"], paramstyle="qmark")
call = "agent trader-1 place_order BUY 50000 GME at market, 40x usual size"
cur = conn.cursor()
cur.execute("SELECT AI_CLASSIFY(?, ['PASS','HOLD','BLOCK']) AS v, "
            "AI_COMPLETE('llama3.3-70b', 'One-line risk reason: ' || ?) AS why", [call, call])
v, why = cur.fetchone()          # OBJECT/VARIANT columns arrive as JSON strings
print(json.loads(v)["labels"][0], "|", why)   # e.g. BLOCK | Order size is 40x normal ...
```
Other SQL functions, with names checked in the Snowpark 1.55.1 source: `AI_FILTER` returns a boolean, `AI_AGG` and `AI_SUMMARIZE_AGG` work across rows, plus `AI_EXTRACT`, `AI_TRANSLATE`, `AI_EMBED`, `AI_SIMILARITY`, `AI_REDACT`, `AI_PARSE_DOCUMENT`, `AI_TRANSCRIBE` and `AI_COUNT_TOKENS`. `AI_COMPLETE(model, prompt, {model_parameters}, {response_format})` returns structured JSON. Model names seen in the SDK source: `llama3.1-8b`, `llama3.3-70b`. Claude ids such as `claude-sonnet-4-5` turn up in search results (unverified per account), so check `/api/v2/cortex/models`.

## Simulation & free sandbox
- The trial is the sandbox: a full account, no card. An X-Small warehouse burns 1 credit/hour, and Cortex calls are billed per token in credits. That's enough for a weekend if you keep auto-suspend at 60 s.
- Free **Marketplace** data: install "Snowflake Public Data (Free)" from Snowsight > Marketplace. It includes daily stock prices and volumes, FX, rates, CPI and SEC filings. One table seen: `SNOWFLAKE_PUBLIC_DATA_FREE.PUBLIC_DATA_FREE.STOCK_PRICE_TIMESERIES` with columns `TICKER, VARIABLE_NAME ('Post-Market Close'...), DATE, VALUE` (search-snippet). Cybersyn's Financial & Economic Essentials listing is also free.
- `Session.builder.config("local_testing", True).create()` runs Snowpark DataFrame code with no account. Cortex AI functions are not emulated (unverified).
- Output shapes: `AI_CLASSIFY` returns `{"labels":["BLOCK"]}`. `AI_SENTIMENT` returns `{"categories":[{"name":"overall","sentiment":"negative"}]}`. `AI_COMPLETE` returns a string, or an object when you pass `response_format`.

## Visualization ideas
- **Streamlit in Snowflake** supervision board (Snowsight > Projects > Streamlit). `get_active_session().sql(...).to_pandas()` feeds `st.bar_chart(df, x="MINUTE", y="N", color="VERDICT")`, giving per-minute PASS/HOLD/BLOCK bars with no hosting.
- An **incident digest card**: `AI_AGG(payload, 'Summarize why these agent calls were blocked')` grouped by desk and day, rendered as text next to the chart.
- A **price + verdict overlay**: join `STOCK_PRICE_TIMESERIES` close prices with the agent's trades and mark BLOCKs on the line.
- A **"ask the auditor" box**: send natural-language questions to Cortex Analyst, and show both the generated SQL and the result table. Judges like seeing the SQL.

## Scenarios (official)
- LLM enrichment of text columns: classify tickets, sentiment of reviews or calls, summarize transcripts, all via `AI_CLASSIFY`, `AI_SENTIMENT`, `AI_AGG` and `AI_SUMMARIZE_AGG` in SQL.
- Natural-language-to-SQL for business users through Cortex Analyst (`/api/v2/cortex/analyst/message`).
- RAG over documents with Cortex Search (`.../cortex-search-services/{name}:query`).
- Agents that orchestrate Analyst and Search tools through Cortex Agents (`agent:run`). The official Snowflake-managed MCP server replaces the deprecated Snowflake-Labs/mcp.
- Financial dashboards on Marketplace data. There is a Cybersyn "Streamlit in Snowflake - Financial Demo" quickstart.
- Calling hosted LLMs from external apps through the Cortex REST API. This is the MLH framing.

## Finance-agent angle
This is a good fit. Use it as the **audit and analytics plane**, not the hot-path gate. Write every tool-call event to an `AGENT_EVENTS` table through the SQL API or connector. Batch-score events with `AI_CLASSIFY` / `AI_COMPLETE(..., response_format)` for PASS/HOLD/BLOCK plus a reason. Run `AI_AGG` for a daily compliance digest. Join with free stock prices for market context. A compliance officer can ask Cortex Analyst "BLOCKs per desk this week?". The pitch: "the LLM runs where the regulated data already lives, under Snowflake governance." For per-call real-time verdicts, call `inference:complete` with `stream:false` instead of a warehouse query (latency unverified).

## Gotchas
- **Trial clock:** the trial ends at $400 or 30 days, whichever comes first, and the account is then suspended until you add a card. Snowflake's education team does not extend trials. Sign up on the day; don't start it a week early.
- **MFA:** Snowflake is phasing out single-factor passwords. In 2026, new human users must use MFA, and service users cannot use passwords. The docs say the phases exclude trial accounts (search-snippet), but Snowsight may still prompt you to enroll. Don't script with `SNOWFLAKE_PASSWORD`; use the PAT, or key-pair for service users.
- **PAT + network policy:** a PAT is rejected without a network policy, and the error looks like "invalid token". The fix is the policy above, or `MINS_TO_BYPASS_NETWORK_POLICY_REQUIREMENT` on the token. The secret is shown once.
- **Cross-region:** frontier models need `CORTEX_ENABLED_CROSS_REGION` (ACCOUNTADMIN only). Pick an AWS US region at signup (unverified that it matters as of Oct 2026).
- **Credits:** warehouses bill per second with a **60 s minimum on every resume**. Set `AUTO_SUSPEND = 60`. An open Streamlit app can keep a warehouse awake (unverified), so close the tab after the demo.
- **Deprecations:** `snowflake.cortex.Complete` and the other `snowflake.cortex.*` helpers are deprecated in snowflake-ml-python 2.4.0; use `snowflake.snowpark.functions.ai_*` or SQL. Legacy `SNOWFLAKE.CORTEX.COMPLETE` / `SENTIMENT` are superseded by `AI_*`, and `AI_SENTIMENT` returns labels, not a float.
- Unquoted identifiers come back UPPERCASE (`df["VERDICT"]`). Multi-statement SQL API calls need `"parameters":{"MULTI_STATEMENT_COUNT":"0"}`. The connector needs Python 3.10+, and Snowpark needs a version below 3.15.

## Mock fallback
`SNOWFLAKE_MODE=mock` (or `DEMO_MODE=1`) swaps in DuckDB 1.5.6 with Python UDFs that share the Snowflake names. The SQL above runs unchanged, because the `?` binds and the `['A','B']` array literal are valid in both. This was tested locally:
```python
import json, duckdb
def mock_conn():
    con = duckdb.connect("fixtures/warehouse.duckdb")
    con.create_function("ai_classify", lambda t, cats: json.dumps({"labels": [cats[2] if "50000" in t else cats[0]]}),
                        ["VARCHAR", "VARCHAR[]"], "VARCHAR")
    con.create_function("ai_complete", lambda m, p: f"[mock {m}] {p[:60]}", ["VARCHAR", "VARCHAR"], "VARCHAR")
    return con
con = mock_conn(); cur = con.cursor()   # keep `con` referenced: a cursor outliving it segfaults
```
For REST calls, record real `inference:complete` and `/statements` JSON into `fixtures/` and replay it (the LLM replay pattern). Use `local_testing` for Snowpark DataFrame logic.

## Sources
- snowflake-connector-python 4.8.0 sdist (`connection.py`: PROGRAMMATIC_ACCESS_TOKEN authenticator, `token`, `paramstyle`) — sdk-source
- snowflake-snowpark-python 1.55.1 wheel (`functions.py`: `ai_*` list and return shapes; `local_testing`) — sdk-source
- snowflake-core 1.13.2 wheel (Cortex REST paths and complete-request fields) and snowflake-ml-python 2.4.0 (`snowflake.cortex` deprecation, AI_* backends) — sdk-source
- https://github.com/PinardKevin/305HACKSHELLS-September2026-MLH-SnowflakeChallenge (`/api/v2/cortex/v1/chat/completions` with Bearer PAT, mlh.link/snowflake-signup) — sdk-source (third-party)
- https://docs.snowflake.com/en/developer-guide/sql-api/submitting-requests, .../programmatic-access-tokens, .../security-mfa-rollout, .../cortex-agents-run, .../cross-region-inference — search-snippet
- https://www.snowflake.com/en/snowflake-trial/ and https://learn.snowflake.com/en/pages/university-faqs/ ($400 / 30 days / no billing info) — search-snippet
- https://www.mlh.com/partners/snowflake (120-day trial link) and mlh.com event prize pages (Arduino Student Kit) — search-snippet
- https://app.snowflake.com/marketplace/listing/GZTSZ290BV255 (Snowflake Public Data Free) — search-snippet
- https://github.com/Snowflake-Labs/mcp (deprecation banner) — sdk-source; pypi.org JSON for all versions — sdk-source

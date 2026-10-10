---
# ---- identity -------------------------------------------------------------
id: tiger-data
name: Tiger Data (TimescaleDB on Tiger Cloud)
provider: Tiger Data (formerly Timescale)
category: database
source: tracks-page
listed_as: "[MLH] Best Use of Tiger Data"
# ---- availability ---------------------------------------------------------
status: active
cost_model: free-tier
free_allowance: "Free plan: 2 free services per account (shared CPU, us-east-1, ~750 MB each (unverified), read-only at the cap), no card. Optional $1000 / 30-day Performance or Scale trial, also no card"
card_required: false
signup_minutes: 5
auth: "Postgres user/password over TLS (sslmode=require); default user tsdbadmin, db tsdb. Tiger CLI: browser OAuth (tiger auth login) or TIGER_PUBLIC_KEY / TIGER_SECRET_KEY"
base_url: "postgres://tsdbadmin:<password>@<service-id>.<project-id>.tsdb.cloud.timescale.com:<port>/tsdb?sslmode=require"
env_vars: [TIGER_DATABASE_URL]
sdks: ["python: psycopg[binary]==3.3.6", "python: asyncpg==0.32.0", "python: sqlalchemy==2.1.4", "python: pgvector==0.5.1", "cli: tiger-cli (curl -fsSL https://cli.tigerdata.com | sh)", "node: @tigerdata/pg-aiguide@0.6.1"]
# ---- simulation -----------------------------------------------------------
sandbox: "Free service is a real DB at $0; `tiger service fork` gives throwaway copies; local Docker timescale/timescaledb-ha:pg18 runs the same engine"
offline_mock: easy
# ---- fit for builders -----------------------------------------------------
demo_effect: 3
integration_hours: "1-3"
risk: low
track_fit: [mlh-tiger-data, hacknc-general, sponsor-finance]
finance_fit: 5
tags: [postgres, time-series, timescaledb, hypertable, continuous-aggregates, ohlcv, agent-events, mcp, pgvector, grafana]
# ---- provenance -----------------------------------------------------------
verified: search-snippet
last_checked: 2026-10-10
docs: ["https://www.tigerdata.com/docs/", "https://github.com/timescale/timescaledb", "https://github.com/timescale/tiger-cli", "https://www.tigerdata.com/pricing"]
---

## TL;DR
Tiger Data is the company formerly called Timescale. It ships TimescaleDB, a Postgres extension for time series, and Tiger Cloud, the hosted version. Any Postgres driver works. The free plan gives you 2 free services with no card, and a 30-day trial with $1000 of credit is also card-free. For the prize, put your agent events and market ticks in **hypertables**, roll them up with **continuous aggregates** and `time_bucket`, and show the speedup live. Start from the current `CREATE TABLE ... WITH (tsdb.hypertable)` syntax. Many older blog posts still use names that have since been deprecated.

## Request structure
Get a service and its connection string, using the CLI or console.cloud.tigerdata.com, then "Download the config":
```bash
curl -fsSL https://cli.tigerdata.com | sh && tiger auth login        # --headless over SSH
tiger service create --name hacknc --cpu shared                       # free service
export TIGER_DATABASE_URL="$(tiger db uri --with-password)"           # postgres://tsdbadmin:...
tiger db query -c "SELECT extversion FROM pg_extension WHERE extname='timescaledb'"
```
Schema for a supervision dashboard. TimescaleDB 2.20+ syntax; the current release is 2.30.2 (2026-09-29):
```sql
CREATE TABLE agent_events (
  ts TIMESTAMPTZ NOT NULL DEFAULT now(), agent_id TEXT NOT NULL, tool TEXT NOT NULL,
  verdict TEXT NOT NULL CHECK (verdict IN ('PASS','HOLD','BLOCK')),
  risk_score DOUBLE PRECISION, payload JSONB
) WITH (tsdb.hypertable, tsdb.segmentby = 'agent_id', tsdb.orderby = 'ts DESC');
-- Classic equivalent: CREATE TABLE ...; SELECT create_hypertable('agent_events', by_range('ts'));
CREATE TABLE ticks (ts TIMESTAMPTZ NOT NULL, symbol TEXT NOT NULL, price DOUBLE PRECISION, volume BIGINT)
  WITH (tsdb.hypertable, tsdb.segmentby = 'symbol');

CREATE MATERIALIZED VIEW verdicts_1m WITH (timescaledb.continuous) AS
SELECT time_bucket('1 minute', ts) AS bucket, agent_id,
       count(*) AS calls, sum((verdict = 'BLOCK')::int) AS blocks, avg(risk_score) AS avg_risk
FROM agent_events GROUP BY bucket, agent_id;
SELECT add_continuous_aggregate_policy('verdicts_1m', start_offset => INTERVAL '1 hour',
  end_offset => INTERVAL '1 minute', schedule_interval => INTERVAL '1 minute');
ALTER MATERIALIZED VIEW verdicts_1m SET (timescaledb.materialized_only = false);  -- include fresh rows

-- OHLCV candles (pattern from the official financial-ticks example)
SELECT time_bucket('5 minutes', ts) AS b, symbol, first(price, ts) AS open, max(price) AS high,
       min(price) AS low, last(price, ts) AS close, sum(volume) AS vol
FROM ticks WHERE ts > now() - INTERVAL '1 day' GROUP BY b, symbol ORDER BY b DESC;
```
Python (psycopg 3; asyncpg takes the same URL):
```python
import os, psycopg
from psycopg.types.json import Jsonb
with psycopg.connect(os.environ["TIGER_DATABASE_URL"], autocommit=True) as conn:
    conn.execute("INSERT INTO agent_events (agent_id, tool, verdict, risk_score, payload) "
                 "VALUES (%s, %s, %s, %s, %s)",
                 ("trader-1", "place_order", "HOLD", 0.72, Jsonb({"symbol": "NVDA", "qty": 500})))
    print(conn.execute("SELECT bucket, agent_id, calls, blocks FROM verdicts_1m "
                       "ORDER BY bucket DESC LIMIT 5").fetchall())
# -> [(datetime.datetime(2026, 10, 10, 18, 4, tzinfo=...), 'trader-1', 1, 0)]
```
Agent tooling: `tiger mcp install claude-code` (also supports cursor, codex, gemini and vscode) adds an MCP server with `service_*` tools plus `db_query` and `db_schema`. It also proxies the **pg-aiguide** docs MCP (`https://mcp.tigerdata.com/docs`, tools `search_docs` and `view_skill`). If you set `TIGER_READ_ONLY=all`, the write tools are never registered.

## Simulation & free sandbox
- Free services cost $0 and run the same engine. `tiger service fork <id>` makes a throwaway copy you can let an agent loose on.
- Synthetic data, all in SQL: `INSERT INTO ticks SELECT g, 'NVDA', 100 + random()*5, (random()*1e4)::int FROM generate_series(now()-'1 day'::interval, now(), '1 second') g;`
- Official sample datasets: S&P 500 1-second ticks over 3 days (~35M rows, `assets.timescale.com/timescaledb-datasets/sp500_stock_prices_3d_1s.tar.gz`), and a crypto tick workshop (~10.7M rows). Both are too big for a free service's storage cap, so load a subset or use local Docker.
- What the output looks like: plain Postgres rows. Candles come back as `(bucket timestamptz, symbol, open, high, low, close, vol)`.

## Visualization ideas
- **Grafana time-series panel** using the official Tiger integration (Postgres data source, Format = Time series). Group with `$__timeGroupAlias(ts, $__interval)`, which emits `time_bucket` once the data source's TimescaleDB toggle is on, and filter with `$__timeFilter(ts)`. Plot a stacked area of `verdicts_1m.blocks` and `calls` per agent.
- **Candlestick panel** (Grafana or a JS chart) fed by the OHLCV query, with BLOCK events overlaid as markers on `ts`.
- **Anomaly band**: compute a z-score of `blocks` over a trailing window (`avg()/stddev() OVER (PARTITION BY agent_id ORDER BY bucket ROWS 30 PRECEDING)`) and highlight buckets where z > 3.
- A **speed split-screen** for judges: run the same 7-day rollup on the raw hypertable and on the cagg with `\timing`, and show both times.

## Scenarios (official)
- Real-time analytics on IoT and sensor data. This is the README quickstart: a hypertable with columnstore, `time_bucket`, and caggs.
- Financial tick and candlestick analysis: OHLCV, SMA, hour-over-hour return and volatility. Covered by `docs/getting-started/financial-ticks` and the TimeSeries-Workshop-Finance repo.
- Application event logging keyed by UUIDv7: `WITH (tsdb.hypertable, tsdb.partition_column='id')`.
- Vector search with pgvector and pgvectorscale (StreamingDiskANN) next to your time-series data.
- "Agentic Postgres": the Tiger CLI and MCP server, forks for agent sandboxes, and the free tier aimed at AI agents.

## Finance-agent angle
This is a strong fit. Every agent tool call becomes a row in an `agent_events` hypertable, and market ticks go in a sibling hypertable. Caggs give per-minute verdict rates and risk per agent. A `JOIN` on `time_bucket` shows "agent bought into a 3-sigma price move". The prize copy says "performance-driven", so show compression (`hypertable_columnstore_stats`) and the cagg speedup. For safety, give the supervising LLM a read-only Tiger MCP and run risky agent SQL on a fork. Both show agent governance with Tiger's own tooling.

## Gotchas
- **Rename debris:** the docs moved to tigerdata.com/docs and the console to console.cloud.tigerdata.com. Old posts use deprecated names. Map them like this: `add_compression_policy`→`add_columnstore_policy`, `compress_chunk`→`convert_to_columnstore`, `timescaledb.compress`→`timescaledb.enable_columnstore`, `compress_segmentby`→`segmentby`.
- **pgai is dead.** As of Feb 2026 it is "no longer maintained or supported" (README). Do embeddings in your app and store them with pgvector instead.
- Free services are in beta: shared CPU, `us-east-1` only, no connection pooler, replicas or metrics exporters, and the service goes read-only at the storage cap. Trial: "we may remove your data" after 30 days unless you add a payment method. Standard services bill while running even when idle, so pause or delete them.
- Caggs are materialized-only by default. Set `materialized_only = false`, or the live demo will show data that is minutes old.
- `CREATE TABLE ... WITH (tsdb.hypertable)` auto-creates a columnstore policy (2.23+). The partition column defaults to the first timestamptz column.
- SQLAlchemy rejects `postgres://`, so rewrite the URL to `postgresql+psycopg://...`. Keep `sslmode=require`.
- Tiger services listen on a non-standard port, and campus Wi-Fi may block it (unverified). Keep a phone hotspot or local Docker ready.
- The `timescaledb-ha:pg18` image is about 680 MB (amd64). Pull it before the event. PG15 support ended in mid-2026.

## Mock fallback
- Same SQL, local engine: `docker run -d --name tsdb -p 6543:5432 -e POSTGRES_PASSWORD=password timescale/timescaledb-ha:pg18`, then `export TIGER_DATABASE_URL=postgres://postgres:password@localhost:6543/postgres`. Only the env var changes. With `DEMO_MODE=1`, the adapter should pick this URL.
- No Docker: plain Postgres 14+ with `date_bin('1 minute', ts, TIMESTAMPTZ '2000-01-03')` in place of `time_bucket`, ordinary tables in place of hypertables, and a regular `MATERIALIZED VIEW` refreshed on a timer in place of the cagg. Guard the `WITH (tsdb.*)` DDL behind a flag.
- Seed with the `generate_series` insert above, or replay a recorded `agent_events.csv` with `\COPY`, so the dashboard has data with Wi-Fi off.

## Sources
- https://github.com/timescale/timescaledb (README quickstart, CHANGELOG 2.30.2, `docs/getting-started/financial-ticks`) — sdk-source
- https://github.com/timescale/tiger-cli (README, `docs/cli/tiger_service_create.md`, `tiger_db_uri.md`) — sdk-source
- https://github.com/timescale/docs (latest branch: `_partials/_cloud-free-trial.md`, `_aws-features.md`, `_services-intro.md`, `api/hypertable/create_table.md`, `integrations/grafana.md`) — official-docs
- https://github.com/timescale/pgai (README deprecation banner), https://github.com/timescale/pg-aiguide — sdk-source
- https://github.com/timescale/TigerData-Workshops/tree/main/TimeSeries-Workshop-Finance — official-docs
- pypi.org JSON (psycopg 3.3.6, asyncpg 0.32.0, SQLAlchemy 2.1.4, pgvector 0.5.1), registry.npmjs.org (@tigerdata/pg-aiguide 0.6.1), hub.docker.com tag pg18 (updated 2026-10-07) — sdk-source
- https://layerbase.com/blog/timescale-alternatives and https://www.g2.com/products/tiger-data/pricing (the ~750 MB free cap, Oct 2025 launch) — search-snippet
- MLH prize copy for Tiger Data, Q3 2026–Q2 2027 (mlh.com events/prizes) — search-snippet

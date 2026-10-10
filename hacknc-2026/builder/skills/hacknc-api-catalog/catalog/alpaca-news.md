---
id: alpaca-news
name: Alpaca Market Data News API (Benzinga)
provider: Alpaca Markets (content by Benzinga)
category: finance-data
source: extra
listed_as: ""
status: active
cost_model: free
free_allowance: "Included with a free Alpaca account; ~200 calls/min (2022 figure, unverified); history back to 2015"
card_required: false
signup_minutes: 10
auth: "Headers APCA-API-KEY-ID + APCA-API-SECRET-KEY (same paper keys)"
base_url: "https://data.alpaca.markets/v1beta1/news"
env_vars: [ALPACA_API_KEY, ALPACA_SECRET_KEY]
sdks: ["python: alpaca-py==0.44.0"]
sandbox: "Real historical news, read-only; no side effects"
offline_mock: easy
demo_effect: 2
integration_hours: "0.5-1"
risk: low
track_fit: [hacknc-general, sponsor-finance]
finance_fit: 5
tags: [news, market-news, tickers, sentiment, research-agent, prompt-injection-test]
verified: sdk-source
last_checked: 2026-10-10
docs: ["https://docs.alpaca.markets/us/docs/historical-news-data", "https://alpaca.markets/blog/introducing-news-api-for-real-time-fiancial-news/"]
---

## TL;DR
Finance-specific news tagged with tickers, with full HTML content and no 24-hour delay, using the same free keys as paper trading. Better than NewsAPI for a market-research agent. Cache it to a JSON file the night before the demo.

## Request structure
`GET https://data.alpaca.markets/v1beta1/news` with params `symbols=AAPL,TSLA`, `start`, `end` (RFC 3339), `limit` (max 50 per page), `sort` (desc|asc), `include_content`, `exclude_contentless`, `page_token`.
Response: `{"news":[{"id","headline","author","created_at","updated_at","summary","content"(HTML),"url","images":[],"symbols":[],"source"}],"next_page_token":...}`.

```bash
curl -G https://data.alpaca.markets/v1beta1/news \
  -H "APCA-API-KEY-ID: $ALPACA_API_KEY" -H "APCA-API-SECRET-KEY: $ALPACA_SECRET_KEY" \
  --data-urlencode "symbols=NVDA,AAPL" --data-urlencode "start=2026-10-03T00:00:00Z" \
  --data-urlencode "limit=50" --data-urlencode "include_content=true"
```
```python
from datetime import datetime, timedelta, timezone
from alpaca.data.historical.news import NewsClient
from alpaca.data.requests import NewsRequest
nc = NewsClient(ALPACA_API_KEY, ALPACA_SECRET_KEY)        # keys are required in 0.44.0
news = nc.get_news(NewsRequest(symbols="AAPL,NVDA,TSLA",
                               start=datetime.now(timezone.utc) - timedelta(days=7),
                               limit=50, include_content=True, exclude_contentless=True))
```

## Simulation & free sandbox
Read-only real data, so "simulation" means replaying cached articles. For a prompt-injection scenario, add one fabricated article to the cache under a clearly fictional source name (not "Benzinga") so it is never mistaken for a real one.

## Visualization ideas
- News feed column with ticker chips; articles the gateway quarantined shown with a hazard stripe and the matched phrase highlighted.
- Ticker × day heatmap of article counts (or sentiment if you score it).
- Hover card: headline, source, and which agent read it.

## Scenarios (official)
- Real-time and historical financial news for trading apps and algorithms (launch blog, historical-news docs).
- Streaming news over WebSocket for real-time strategies.

## Finance-agent angle
Core input for a research agent, and the natural carrier for an indirect prompt-injection test (an article that tells the agent to email client data). The gateway scans tool output before it reaches the model.

## Gotchas
- README says `NewsClient()` works without keys; in 0.44.0 it raises `ValueError: You must supply a method of authentication`.
- Without `limit` the SDK pages until results run out.
- `start` defaults to the start of the current day; on a Saturday that returns almost nothing, so always set it.
- `content` is HTML; strip tags before showing or scanning.

## Mock fallback
`fixtures/news_cache.json` with the exact response schema; the research agent reads the cache by default (`NEWS_MODE=cache|live`).

## Sources
- https://raw.githubusercontent.com/alpacahq/alpaca-py/master/alpaca/data/historical/news.py and `alpaca/data/requests.py` (sdk-source)
- https://github.com/alpacahq/alpaca-docs `api-references/market-data-api/news-data/historical.md` (official-docs, archived)
- https://alpaca.markets/blog/introducing-news-api-for-real-time-fiancial-news/ (search-snippet)

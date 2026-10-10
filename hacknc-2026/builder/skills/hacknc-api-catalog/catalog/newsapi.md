---
# ---- identity -------------------------------------------------------------
id: newsapi
name: NewsAPI (newsapi.org)
provider: NewsAPI.org
category: news
source: resources-doc
listed_as: "NewsAPI"
# ---- availability ---------------------------------------------------------
status: active
cost_model: free-tier
free_allowance: "Developer plan: 100 req/day, articles delayed 24h, search back 1 month, localhost-only CORS, dev/testing only; next tier Business $449/mo"
card_required: false
signup_minutes: 3
auth: "Header X-Api-Key: <key> (or ?apiKey=<key>)"
base_url: "https://newsapi.org/v2"
env_vars: [NEWSAPI_KEY, NEWS_MODE]
sdks: ["python: newsapi-python==0.2.7 (unofficial, last release 2023)", "node: newsapi@2.4.1 (unofficial)", "python: requests==2.34.2 (simplest)"]
# ---- simulation -----------------------------------------------------------
sandbox: "none; the free Developer key is the sandbox (100 req/day). Cache every response to fixtures/"
offline_mock: easy
# ---- fit for builders -----------------------------------------------------
demo_effect: 2
integration_hours: "0.5-1"
risk: low
track_fit: [hacknc-general, hacknc-beginner, sponsor-finance]
finance_fit: 2
tags: [news, headlines, search, sentiment, rag, monitoring]
# ---- provenance -----------------------------------------------------------
verified: search-snippet
last_checked: 2026-10-10
docs: ["https://newsapi.org/docs/get-started", "https://newsapi.org/docs/endpoints/everything", "https://newsapi.org/docs/endpoints/top-headlines", "https://newsapi.org/docs/errors", "https://newsapi.org/pricing"]
---

## TL;DR
A keyword search over general-press articles and headlines. One GET with a header key, and signup takes about 3 minutes. The free Developer plan has three catches: **articles arrive 24 hours late**, you get **100 requests a day**, and browser calls only work from localhost. Fine for "what has the press said about X this month" context or RAG. Not a live market feed: for finance use `alpaca-news` (Benzinga, ticker-tagged, real time) and keep NewsAPI for broad coverage.

## Request structure
- **`GET /v2/everything`** searches all articles.
  - `q`: up to 500 chars. Supports `"exact phrase"`, `+must`, `-exclude`, `AND`/`OR`/`NOT` and parentheses.
  - `qInTitle`, `searchIn` (`title,description,content`; unverified).
  - `sources` (comma ids), `domains`, `excludeDomains`.
  - `from` / `to` (ISO 8601), `language` (`en` …).
  - `sortBy` = `relevancy` | `popularity` | `publishedAt`, `pageSize` ≤ 100, `page`.
- **`GET /v2/top-headlines`** returns current headlines.
  - `country`, `category` (business, technology, …), `sources`, `q`, `pageSize`, `page`.
  - `sources` cannot be combined with `country`/`category`.
- **`GET /v2/top-headlines/sources`** lists source ids (`id, name, category, country, url`).
- **Auth:** `X-Api-Key` header (preferred), `apiKey` query param, or `Authorization: <key>`.
- **Response:** `{status:"ok", totalResults, articles:[{source:{id|null, name}, author, title, description, url, urlToImage, publishedAt, content}]}`. `content` is cut to about 200 chars and ends with "[+N chars]" (unverified).
- **Errors:** `{status:"error", code, message}`. Codes include `apiKeyInvalid`/`apiKeyMissing` (401), `rateLimited` (429), `parameterInvalid` (400), and `maximumResultsReached` (more than 100 results on the free plan; unverified).

```bash
curl -s "https://newsapi.org/v2/everything?q=%22interest%20rates%22%20AND%20(Fed%20OR%20FOMC)&language=en&sortBy=publishedAt&pageSize=20" \
  -H "X-Api-Key: $NEWSAPI_KEY" | jq '{total: .totalResults, first: (.articles[0] | {title, source: .source.name, publishedAt})}'
```
```python
import os, requests
def search_news(q: str, page_size: int = 20, **extra) -> list[dict]:
    r = requests.get("https://newsapi.org/v2/everything",
                     headers={"X-Api-Key": os.environ["NEWSAPI_KEY"]},
                     params={"q": q, "language": "en", "sortBy": "publishedAt",
                             "pageSize": page_size, **extra}, timeout=10)
    body = r.json()
    if body.get("status") != "ok":
        raise RuntimeError(f"{body.get('code')}: {body.get('message')}")
    return body["articles"]
# Unofficial SDK: NewsApiClient(api_key=...).get_everything(q=..., from_param="2026-10-01",
#   sort_by="publishedAt", page_size=20)  # note from_param / sort_by / page_size names
```

## Simulation & free sandbox
There is no test mode. The free Developer key returns real data under the plan limits: 100 requests/day, a 24h delay, one month of history, and dev/testing use only. Simulate by recording real responses once into `fixtures/news/*.json` and replaying them (see Mock fallback). A plan-limit error looks like `{"status":"error","code":"rateLimited","message":"You have made too many requests recently…"}` (message text unverified).

## Visualization ideas
- **Headline ticker or cards** with an LLM-assigned sentiment chip and an entity chip. Fields: `title`, `source.name`, `publishedAt`, `urlToImage`.
- **Event markers on a price or agent-activity chart:** a vertical pin at each `publishedAt`. Clicking it shows which agent decision cited that `url`.
- **Source-mix bar chart** (`source.name` counts), so a judge can see the agent isn't reading a single outlet.
- **Evidence panel in an agent trace:** each reasoning step lists the article titles and links it used.

## Scenarios (official)
- Search worldwide news and blog articles by keyword, phrase, source, domain or date (`/v2/everything`).
- Get live top and breaking headlines by country, category or source (`/v2/top-headlines`).
- List available publishers to build source filters (`/v2/top-headlines/sources`).
- Brand or company monitoring, i.e. tracking mentions of a name over time (inferred, via `/v2/everything` sorted by `publishedAt`).

## Finance-agent angle
**Weak-to-moderate fit.** It's useful as **context**:
- "What is the press saying about Capital One this week?"
- Macro headlines feeding a risk agent's rationale.
- A news-grounded explanation layer on an agent-monitoring dashboard ("why did the agent de-risk on Oct 8?").

It has limits: no ticker tagging, no real-time data on the free plan, and the free plan isn't for production. For market-moving news use `catalog/alpaca-news.md`. A good pattern is Alpaca for tickers plus NewsAPI for general-press colour.

## Gotchas
- **24h delay on the free plan.** Today's articles (Oct 10) won't appear until tomorrow. Never claim "live news" in the demo. Whether `top-headlines` is also delayed is unverified.
- **100 requests/day.** A 60-second polling loop uses it up in under 2 hours. Cache by query and fetch on demand.
- **CORS is allowed only from localhost.** A deployed frontend gets blocked, so call from your backend.
- **Developer plan terms say development/testing only.** A hackathon demo is fine; a public launch isn't.
- **`content` is truncated.** Fetch `url` yourself for full text, which may be paywalled.
- **Result caps:** `pageSize` max 100. Free accounts reportedly can't page past the first 100 results (unverified).
- **`newsapi-python` quirks:** it is unofficial and stale, `get_top_headlines` defaults `language="en"`, and the date parameter is `from_param`.
- **Top-headlines coverage by `country` has reportedly shrunk** to a few countries (unverified). Prefer `/everything` with `domains=` for specific outlets.

## Mock fallback
- **Adapter:** `adapters/news.py` with `NEWS_MODE=cache|live`.
- **Live mode** returns the provider's own JSON and writes it to `fixtures/news/<sha1(query)>.json`.
- **Cache mode** reads those fixtures and **shifts `publishedAt` so the newest article is "now minus a few minutes"**. The timeline then looks fresh in the demo.
- **For scripted scenes**, hand-write 10–20 articles tied to the demo storyline (e.g. "Regulator fines bank over AI trading controls"), or generate them with `faker` plus an LLM. Use the same `articles[]` shape.

## Sources
- https://newsapi.org/pricing (search-snippet: Developer free, Business $449/mo, Advanced $1,749/mo, 250k req/mo on Business; 100 req/day, 24h delay, 1-month search, localhost CORS)
- https://newsapi.org/docs/endpoints/everything and /top-headlines (search-snippet + caller-verified earlier today: params, pageSize ≤ 100, q ≤ 500 chars)
- https://newsapi.org/docs/errors (search-snippet: parameterInvalid, rateLimited)
- https://pypi.org/project/newsapi-python/0.2.7/ (sdk-source: method/param names, endpoints, Authorization header, language default)
- https://registry.npmjs.org/newsapi/latest (sdk-source: 2.4.1)
- searchIn, maximumResultsReached, content truncation length, country coverage (memory)

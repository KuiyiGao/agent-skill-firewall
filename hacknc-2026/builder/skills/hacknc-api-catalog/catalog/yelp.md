---
# ---- identity -------------------------------------------------------------
id: yelp
name: Yelp Places API (formerly Fusion) + Yelp AI API
provider: Yelp Inc.
category: local-business
source: resources-doc
listed_as: "Yelp"
# ---- availability ---------------------------------------------------------
status: changed
cost_model: free-trial
free_allowance: "30-day trial, up to 5,000 calls total, evaluation only (no public launch); then Base $229/mo, Enhanced $299, Premium $643"
card_required: unknown
signup_minutes: 15
auth: "Header Authorization: Bearer <API key>"
base_url: "https://api.yelp.com/v3"
env_vars: [YELP_API_KEY, YELP_MODE]
sdks: ["python: requests==2.34.2 (no official Python SDK)", "python: yelpapi==2.6.0 (unofficial)", "mcp: github.com/Yelp/yelp-mcp 0.1.0 (official example MCP server for the AI API)"]
# ---- simulation -----------------------------------------------------------
sandbox: "none; the 30-day / 5,000-call trial key is the only free path (email fusion@yelp.com to extend)"
offline_mock: easy
# ---- fit for builders -----------------------------------------------------
demo_effect: 3
integration_hours: "1-2"
risk: medium
track_fit: [hacknc-general, hacknc-community, hacknc-ig-turing]
finance_fit: 2
tags: [local-business, places, reviews, restaurants, maps, ai-agent, mcp, merchant-enrichment]
# ---- provenance -----------------------------------------------------------
verified: search-snippet
last_checked: 2026-10-10
docs: ["https://docs.developer.yelp.com/docs/places-intro", "https://docs.developer.yelp.com/docs/places-faq", "https://business.yelp.com/data/resources/pricing/", "https://docs.developer.yelp.com/reference/v2_ai_chat", "https://github.com/Yelp/yelp-mcp"]
---

## TL;DR
The old free "Fusion API" is now the paid **Yelp Places API**. Free access ended in 2024. The only free path is a **30-day trial with up to 5,000 calls, for evaluation only**, started by creating an app at yelp.com/developers/v3/manage_app. Searches return businesses with ratings, price, categories and coordinates, which makes a good map demo. There is also a conversational **Yelp AI API** (`POST /ai/chat/v2`) with an official MCP server, so it fits naturally as a "sub-agent" an orchestrator calls. Finance fit is weak.

## Request structure
- **`GET /v3/businesses/search`**
  - Location: `term`, plus `location` or `latitude`+`longitude`.
  - Filters: `categories`, `price=1,2`, `open_now`, `radius` (≤ 40000 m).
  - Ordering and paging: `sort_by` = best_match | rating | review_count | distance, `limit` ≤ 50, `offset` (limit+offset ≤ 240; unverified).
- **`GET /v3/businesses/{id_or_alias}`** returns details (hours; photos depend on plan).
- **`GET /v3/businesses/{id}/reviews`** returns review excerpts. **Enhanced or Premium plans only** (3 or 7 excerpts).
- **`GET /v3/autocomplete?text=&latitude=&longitude=`**
- **Search response:**
  - Top level: `{businesses:[…], total, region:{center:{latitude, longitude}}}`.
  - Each business: `id, alias, name, image_url, is_closed, url, review_count, categories:[{alias, title}], rating, coordinates:{latitude, longitude}, transactions, price, location:{address1, city, zip_code, display_address[]}, phone, display_phone, distance`.
- **AI API:** `POST https://api.yelp.com/ai/chat/v2`, same Bearer key, JSON `{query, chat_id?, user_context?:{latitude, longitude}}`.
  - Response: `{response:{text}, chat_id, entities:[{businesses:[{name, rating, review_count, price, categories, location:{formatted_address}, coordinates, url, phone, attributes, contextual_info:{business_hours, review_snippets, photos}, summaries:{short, long}}]}]}`. Shape taken from Yelp's own MCP source.

```bash
curl -s "https://api.yelp.com/v3/businesses/search?term=coffee&latitude=35.9132&longitude=-79.0558&limit=10&sort_by=rating" \
  -H "Authorization: Bearer $YELP_API_KEY" | jq '.businesses[] | {name, rating, review_count, price, coordinates}'
```
```python
import os, requests
H = {"Authorization": f"Bearer {os.environ['YELP_API_KEY']}"}
def search(term: str, lat=35.9132, lon=-79.0558, limit=20) -> list[dict]:     # UNC Chapel Hill
    r = requests.get("https://api.yelp.com/v3/businesses/search", headers=H, timeout=10,
                     params={"term": term, "latitude": lat, "longitude": lon, "limit": limit})
    r.raise_for_status()
    return r.json()["businesses"]

def ask_yelp_ai(query: str, chat_id: str | None = None) -> dict:    # multi-turn via chat_id
    body = {"query": query, **({"chat_id": chat_id} if chat_id else {}),
            "user_context": {"latitude": 35.9132, "longitude": -79.0558}}
    r = requests.post("https://api.yelp.com/ai/chat/v2", headers=H, json=body, timeout=30)
    r.raise_for_status()
    return r.json()          # .response.text, .chat_id, .entities[0].businesses
```

## Simulation & free sandbox
- There is no sandbox or test key.
- The trial key returns real data and is the only free option: 30 days, up to 5,000 calls total, "strictly for evaluation and not for commercial deployment".
- The official MCP README says to email fusion@yelp.com for a longer trial.
- Spend trial calls only on capturing fixtures and on the final demo. Everything else runs on the mock.
- When you go over a limit you get HTTP 429. Remaining-quota headers are returned on each response (header names unverified).

## Visualization ideas
- **Map with pins** (Leaflet/Mapbox). Position from `coordinates`, colour from `rating`, radius from `review_count`, popup with `image_url`.
- **Price vs rating scatter**, using `price` ($–$$$$) on the x-axis and `rating` on the y-axis, bubble size `review_count`. Shows which spots are good value.
- **Category treemap** from `categories[].title` counts, e.g. "what's around campus".
- **Agent-to-agent trace (AI API):** chat bubbles grouped by `chat_id`, each answer followed by business cards from `entities[].businesses`.

## Scenarios (official)
- Local search and discovery by keyword, category, location and price (`/v3/businesses/search`).
- Business details, hours and photos (`/v3/businesses/{id}`). Review excerpts on Enhanced/Premium plans (`/v3/businesses/{id}/reviews`).
- Search-as-you-type (`/v3/autocomplete`).
- Natural-language search, multi-turn follow-ups, direct business questions, comparisons and itineraries (`/ai/chat/v2`, per the Yelp MCP README).
- Conversational restaurant reservations, on request only (`/ai/chat/v2`).

## Finance-agent angle
**Weak fit.** Two honest angles:
1. **Merchant enrichment for a personal-finance agent.** Map transaction merchant names (e.g. from `capital-one-nessie` mock data) to Yelp categories and coordinates. Then show a "where your money goes" map, or flag an odd merchant category. This is inferred, and Yelp's terms may restrict storing or analysing content (unverified).
2. **Agent-monitoring demo with Yelp AI as an observed sub-agent.** An orchestrator delegates "book a client dinner under $40/person" to Yelp AI. The dashboard shows each call, its latency, `chat_id` threading, and whether the result broke a policy (budget, distance).

Do not use it for credit or small-business underwriting signals. That is not an official use case and the terms likely forbid it (unverified).

## Gotchas
- **No free tier anymore.** The trial is 30 days and 5,000 calls total, then plans start at $229/mo. Blogs that say "5,000 calls/day free" are from before 2024.
- **Trial signup** reportedly asks for a business email and a Yelp user account. Whether a unc.edu address counts is unverified. Card requirement is unknown. Sign up early.
- **Reviews endpoint** requires Enhanced/Premium. Which plan the trial maps to is unverified, so expect possible 403s and build without reviews.
- **AI API access and limits** are unclear. A third-party source says Premium-only with about 20 calls/day (unverified). Test on the first call.
- **No browser CORS** (unverified). Call from your backend; never ship the key to the frontend.
- **Display rules:** show Yelp attribution and link to each business `url` (from memory, unverified for 2026).
- **Data quirks:** `rating` goes in 0.5 steps, `price` is often missing, `distance` is in metres. `limit` > 50 returns a 400.

## Mock fallback
- **Adapter:** `adapters/places.py` with `YELP_MODE=cache|live`. Live mode saves each response to `fixtures/yelp/<query>.json`.
- **Seed data:** capture 2–3 searches around Franklin St / UNC once, or generate about 30 fake businesses. Use seeded coordinates within 1 km of 35.9132,-79.0558, ratings from 3.0 to 5.0, and price $–$$$, all in the exact `businesses[]` shape.
- **AI API mock:** returns canned `{response:{text}, chat_id:"mock-1", entities:[{businesses:[…]}]}` keyed by query text, so the agent trace UI works offline.

## Sources
- https://docs.developer.yelp.com/docs/places-intro (search-snippet: endpoints, base URL, Bearer auth)
- https://docs.developer.yelp.com/docs/places-faq and https://business.yelp.com/data/resources/pricing/ (search-snippet: 30-day / 5,000-call trial, evaluation only, Base/Enhanced/Premium prices, business email)
- https://docs.developer.yelp.com/reference/v3_business_reviews (search-snippet: Enhanced/Premium required)
- https://github.com/Yelp/yelp-mcp (sdk-source: `POST https://api.yelp.com/ai/chat/v2`, body `query/chat_id/user_context`, response fields, trial extension email)
- https://github.com/Yelp/yelp-fusion (sdk-source: sample uses `/v3/businesses/search`, Bearer header; unofficial client list)
- https://pypi.org/pypi/yelpapi/json (sdk-source: 2.6.0)
- https://supergood.ai/api-report-card/yelp and https://vorplabs.com/agent-tools/yelp-ai-api (search-snippet, third-party: free access ended July 2024; AI API Premium-only, 20/day)
- limit+offset ≤ 240, attribution rules, CORS (memory)

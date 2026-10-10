# Integration patterns for hackathon builds

These patterns exist because a hackathon demo fails for boring reasons: venue Wi-Fi, a
free-tier quota hit during rehearsal, a faucet returning 429, a model that answers
differently the tenth time. Each external API should be swappable for a local stand-in
without touching the code that uses it.

## 1. Mock-first adapter (one interface, several backends)

Every external dependency gets a small adapter with a `MODE` switch read from the
environment. Write the mock first (minutes), build the UI against it, then add `live`.

```python
# adapters/news.py
import json, os, pathlib
MODE = os.getenv("NEWS_MODE", "cache")          # cache | live
CACHE = pathlib.Path("fixtures/news_cache.json")

def get_news(symbols: list[str], days: int = 7) -> list[dict]:
    if MODE == "live":
        items = _fetch_live(symbols, days)      # real API call, same output shape
        CACHE.write_text(json.dumps(items, indent=1))   # refresh the cache as a side effect
        return items
    return [n for n in json.loads(CACHE.read_text()) if set(n["symbols"]) & set(symbols)]
```

Conventions:
- Env var per adapter: `NEWS_MODE`, `BROKER` (alpaca|mock), `VOICE_MODE` (live|cache|off),
  `ANCHOR_MODE` (devnet|local), `LLM_MODE` (live|replay). One global `DEMO_MODE=1` can
  force every adapter to its offline value.
- The mock returns **the provider's own response shape**, so switching is invisible to callers.
- `live` mode writes what it receives into `fixtures/` so the cache improves as you build.

## 2. Stub server when the SDK takes a base URL

Some SDKs accept a base-URL override (e.g. `TradingClient(url_override=...)` in alpaca-py).
Then the cheapest mock is a tiny FastAPI app serving the same paths and JSON, so the real
SDK code path is exercised end to end.

## 3. Replay cache for LLM turns

Record model responses for each scripted demo scenario and replay them by request hash.

```python
import hashlib, json, pathlib
def key(messages, tools) -> str:
    blob = json.dumps({"m": messages, "t": [t["name"] for t in tools]}, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]
# live: call the API, save fixtures/llm/<key>.json; replay: load it, fail loudly if missing
```
Replay keeps the demo identical every time and makes it work offline. Keep live mode for
the Q&A ("ask it anything").

## 4. Secrets and env

- Keep keys in `.env` (git-ignored); commit `.env.example` with every variable name.
  `python scripts/catalog.py env` prints the variable names used across the catalog.
- Never put keys in frontend code; browser calls go through your backend, except APIs
  designed for public browser keys (map tiles with referrer-restricted keys, ElevenLabs
  public agents).
- Solana keypair files are secrets; commit only the public key.

## 5. Event bus for live dashboards

Backend publishes one JSON event per action to an in-process queue; the browser
subscribes with Server-Sent Events (one `GET /events` with `text/event-stream`). SSE is
simpler than WebSockets for one-way updates and reconnects automatically.

```python
# FastAPI
from fastapi.responses import StreamingResponse
async def events():
    async def gen():
        q = bus.subscribe()
        while True:
            ev = await q.get()
            yield f"data: {json.dumps(ev)}\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")
```
```js
new EventSource("/events").onmessage = (m) => render(JSON.parse(m.data));
```

## 6. Demo-day checklist for any API

- Account created, key in `.env`, one successful live call logged **the day before**.
- Quota math: calls per rehearsal × rehearsals ≤ free allowance.
- Fixture captured for every scene; `DEMO_MODE=1` run passes with Wi-Fi off.
- Rate-limited resources (faucets, trial SMS) pre-provisioned.
- Clean-up step known (e.g. cancel queued paper orders).

---
# ---- identity -------------------------------------------------------------
id: x-api
name: X API v2 (formerly Twitter API)
provider: X Corp.
category: social
source: resources-doc
listed_as: "Twitter’s APIs"
# ---- availability ---------------------------------------------------------
status: changed
cost_model: paid-only
free_allowance: "No free tier for new developers (pay-per-use since Feb 2026). ~$0.005/post read, $0.010/user read, $0.015/post created, $0.20/post with a URL; $20 credit for saving a first card (expires in 3 months)"
card_required: true
signup_minutes: 20
auth: "Reads: Authorization: Bearer <app bearer token>. Writes: OAuth 1.0a user context or OAuth 2.0 PKCE user token"
base_url: "https://api.x.com/2"
env_vars: [X_BEARER_TOKEN, X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET, X_MODE]
sdks: ["python: xdk==0.10.6 (official, alpha)", "python: tweepy==4.17.0", "node: @xdevplatform/xdk@0.6.6", "node: twitter-api-v2@1.29.1"]
# ---- simulation -----------------------------------------------------------
sandbox: "none; no test mode. Set a small spend cap in console.x.com; failed requests are not billed"
offline_mock: easy
# ---- fit for builders -----------------------------------------------------
demo_effect: 3
integration_hours: "1-3"
risk: high
track_fit: [hacknc-general, hacknc-ig-turing]
finance_fit: 2
tags: [social, posts, search, sentiment, cashtags, bot, publishing, cost-tracking]
# ---- provenance -----------------------------------------------------------
verified: search-snippet
last_checked: 2026-10-10
docs: ["https://docs.x.com/x-api/introduction", "https://docs.x.com/x-api/getting-started/pricing", "https://docs.x.com/x-api/getting-started/free-credits", "https://docs.x.com/x-api/fundamentals/post-cap", "https://github.com/xdevplatform/xdk-python"]
---

## TL;DR
The legacy Free tier (and Basic/Pro for new signups) is gone. Since **Feb 2026 the X API is pay-per-use**: buy credits in the Developer Console (console.x.com) and each successful request draws them down. Saving a first card earns **$20 of free credit**, and X matches your first auto-recharge up to $50. A demo-scale budget is cheap: 100 post reads cost about $0.50. Still, a card is mandatory and there is no sandbox. The official Python SDK is **xdk**, and its README example has the wrong constructor (see Gotchas).

## Request structure
- **Recent search (last 7 days):** `GET /2/tweets/search/recent`.
  - Params: `query`, `max_results` (10–100), `tweet.fields=created_at,public_metrics,author_id,lang`, `expansions=author_id`, `user.fields=username`, `next_token`, `start_time`, `end_time`, `sort_order=recency|relevancy`.
  - Operators: `lang:en`, `-is:retweet`, `from:`, `has:links`, and cashtag `$NVDA` (cashtag availability on pay-per-use is unverified).
  - Auth: app Bearer token.
- **Search response:**
  - Top level: `{data:[…], includes:{users:[…]}, meta:{newest_id, oldest_id, result_count, next_token}}`.
  - Each post: `id, text, created_at, author_id, public_metrics:{retweet_count, reply_count, like_count, quote_count, bookmark_count, impression_count}`.
- **Create post:** `POST /2/tweets`, JSON `{"text": "…"}`, user-context auth, returns 201 `{data:{id, text}}`. The request body also accepts `reply`, `quote_tweet_id`, `poll`, `media` and `made_with_ai`.
- **Usage:** `GET /2/usage/tweets` returns post consumption. Pair it with a cost meter.
- **News:** `GET /2/news/search?query=&max_results=&max_age_hours=` returns X's curated news stories (in xdk; price and access unverified).
- **Errors:** 401 for bad tokens; 402 or "no credits" once the balance is used up (forum reports); 429 with `x-rate-limit-remaining` / `x-rate-limit-reset` headers.

```bash
curl -s "https://api.x.com/2/tweets/search/recent?query=%24NVDA%20lang%3Aen%20-is%3Aretweet&max_results=10&tweet.fields=created_at,public_metrics" \
  -H "Authorization: Bearer $X_BEARER_TOKEN" | jq '.data[] | {id, created_at, likes: .public_metrics.like_count, text}'
```
```python
import os
from xdk import Client
from xdk.oauth1_auth import OAuth1

reader = Client(bearer_token=os.environ["X_BEARER_TOKEN"])
pages = reader.posts.search_recent(query="$NVDA lang:en -is:retweet", max_results=10,
                                   post_fields=["created_at", "public_metrics", "author_id"])
page = next(pages)                    # generator auto-paginates: take ONE page or pay for every page
for p in page.data or []:
    print(p.id, p.created_at, p.text[:80])

writer = Client(auth=OAuth1(api_key=os.environ["X_API_KEY"], api_secret=os.environ["X_API_SECRET"],
                            callback="oob", access_token=os.environ["X_ACCESS_TOKEN"],
                            access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"]))
writer.posts.create(body={"text": "Agent status: all positions within risk limits."})   # $0.015; no URLs ($0.20)
```

## Simulation & free sandbox
- There is no test environment. Every successful call is real and billed.
- **Cost controls:**
  - Set a **spending limit** per billing cycle; requests are blocked once it is reached.
  - Only successful responses that return data are billed.
  - Identical resources are **deduplicated within a 24h UTC day**, so re-running the same search during rehearsal doesn't re-bill posts already returned today.
  - Owned reads (your own account's data) cost $0.001.
- **Free credits:** $20 for saving a first eligible card, plus a match of your first auto-recharge up to $50. Both expire 3 months after they are granted.
- **Login with X** (OAuth) endpoints are free.
- For anything else, use the mock below.

## Visualization ideas
- **Mention-volume time series per cashtag:** bucket `created_at` per 15 min and overlay `public_metrics.like_count` as engagement.
- **Sentiment stream:** posts flow into a lane coloured by an LLM bull/bear/neutral label, with a rolling average gauge.
- **Outbound-action audit** for an agent that posts: draft → policy/compliance check → human approve → posted `data.id`, or blocked. Status chips per step.
- **Live API cost meter:** count of reads × $0.005 plus posts × $0.015, or `/2/usage/tweets`. Fits an "agent monitoring" dashboard that shows agent spend as it happens.

## Scenarios (official)
- Publish posts, replies, polls and media from bots or apps (`POST /2/tweets`, `/2/media`).
- Search and social listening: recent (`/2/tweets/search/recent`) and full archive (`/2/tweets/search/all`).
- Real-time filtered stream (`/2/tweets/search/stream`).
- Users, followers, lists, likes, bookmarks, DMs (`/2/users/...`, `/2/dm_*`).
- Trends, Spaces, Communities, Community Notes, News (`/2/news/search`), and account activity webhooks (all in the xdk module list).

## Finance-agent angle
**Weak-to-moderate fit.**
- **Reads:** cashtag sentiment and volume spikes can feed a market-monitoring agent ("social chatter on $XYZ tripled in 30 min"). The data is noisy, covers only 7 days, and every read is paid.
- **Writes:** an agent that drafts public updates for a financial firm is a good **compliance / human-in-the-loop story**. The dashboard shows the policy check and the approval gate before the post goes out. Keep the real post off, or post to a throwaway account.

Real-time market news is better served by `alpaca-news`.

## Gotchas
- **A card is required.** Blogs and old docs that mention "Free: 500 posts / 100 reads per month" are stale for new accounts.
- **Read caps:** a monthly cap of 2M or 3M post reads (the docs disagree). Irrelevant at hackathon scale.
- **A post containing a URL costs $0.20**, about 13× a plain post. Keep links out of bot posts.
- **xdk 0.10.6 README is wrong.** It shows `Client(api_key=..., access_token_secret=...)`, but the real constructor takes `bearer_token`, `access_token` (an OAuth2 user token), `client_id`/`client_secret`/`redirect_uri` for PKCE, or `auth=OAuth1(...)`. `OAuth1` requires a `callback` argument; `"oob"` works for pre-generated tokens.
- **xdk `search_recent` is a generator that keeps paginating.** Iterating it in a `for` loop can drain credits. Use `next()` or break.
- **Field-parameter naming:** xdk sends the query param as `post.fields`, while classic docs use `tweet.fields`. Both are presumably accepted (unverified). The curl above uses `tweet.fields`.
- **Write permissions:** set the app to Read+Write *before* generating the access token and secret; changing it later means regenerating them (memory).
- **Rate limits:** 15-minute windows still apply on top of billing, and you get 429s when you exceed them.
- **AI-generated posts:** the request body has a `made_with_ai` flag. Follow X's automation rules.

## Mock fallback
- **Adapter:** `adapters/social.py` with `X_MODE=mock|live`, plus a `SocialFeed` interface: `search(query, n) -> {data, includes, meta}` and `post(text) -> {data:{id, text}}`.
- **Mock search data:** about 200 synthetic posts (LLM- or faker-generated). Each has cashtags, `created_at` spread over the last 6 h and shifted to "now" at load time, random `public_metrics`, and a hidden seeded sentiment, so the charts show a planned spike.
- **Mock `post()`** appends to `fixtures/x_outbox.json`. The UI renders it as an X-style card labelled "simulated".
- **Live capture:** with a few dollars of credit, capture one real page per demo query into fixtures for authenticity.

## Sources
- https://docs.x.com/x-api/getting-started/pricing (search-snippet: per-resource rates, owned reads $0.001, 24h dedup, failed requests unbilled, spending limits, 3M cap)
- https://docs.x.com/x-api/fundamentals/post-cap (search-snippet: 2M cap, conflicting)
- https://docs.x.com/x-api/getting-started/free-credits (search-snippet: $20 card + up to $50 match, 3-month expiry)
- https://devcommunity.x.com/t/no-free-plan/257026 and https://docs.x.com/changelog (search-snippet: Free tier deprecated, $10 voucher for legacy Free users, Login with X free, console.x.com)
- Third-party summaries dated 2026, e.g. https://www.socialcrawl.dev/blog/x-twitter-api-2026 (search-snippet: Feb 6 2026 switch, Pro deprecation Aug 2026)
- https://pypi.org/project/xdk/0.10.6/ (sdk-source: Client signature, OAuth1(callback), search_recent generator + `post.fields`, `/2/tweets`, `/2/usage/tweets`, `/2/news/search`, CreatePostsRequest fields)
- https://pypi.org/pypi/tweepy/json, https://registry.npmjs.org/@xdevplatform/xdk/latest, https://registry.npmjs.org/twitter-api-v2/latest (sdk-source: versions)
- Read+Write token regeneration, cashtag operator availability (memory)

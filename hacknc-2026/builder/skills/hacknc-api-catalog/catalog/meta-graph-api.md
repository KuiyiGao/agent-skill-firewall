---
# ---- identity -------------------------------------------------------------
id: meta-graph-api
name: Meta Graph API (WhatsApp Cloud API, Facebook Pages, Instagram)
provider: Meta Platforms, Inc.
category: social
source: resources-doc
listed_as: "Facebook for Developers"
# ---- availability ---------------------------------------------------------
status: active
cost_model: free
free_allowance: "Graph API calls free (rate-limited); WhatsApp Cloud API test number free, up to 5 verified recipients, no payment method needed"
card_required: false
signup_minutes: 20
auth: "Authorization: Bearer <user | page | system-user token> (or ?access_token=)"
base_url: "https://graph.facebook.com/v26.0"
env_vars: [META_APP_ID, META_APP_SECRET, META_PAGE_ID, META_PAGE_TOKEN, WA_PHONE_NUMBER_ID, WA_TOKEN, WA_TO_NUMBER, WA_VERIFY_TOKEN, META_MODE]
sdks: ["python: facebook-business==26.0.2 (Graph/Marketing API v26.0)", "node: facebook-nodejs-business-sdk@24.0.1", "python: requests==2.34.2 (simplest for WhatsApp/Pages)"]
# ---- simulation -----------------------------------------------------------
sandbox: "Development mode (app-role users get every permission without App Review), Graph API Explorer, WhatsApp test phone number (free, up to 5 recipients), test users via /{app-id}/accounts/test-users"
offline_mock: easy
# ---- fit for builders -----------------------------------------------------
demo_effect: 3
integration_hours: "2-4"
risk: medium
track_fit: [hacknc-general, hacknc-community]
finance_fit: 2
tags: [social, whatsapp, facebook, instagram, messaging, alerts, approval, pages, insights, webhooks]
# ---- provenance -----------------------------------------------------------
verified: search-snippet
last_checked: 2026-10-10
docs: ["https://developers.facebook.com/docs/graph-api", "https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started", "https://developers.facebook.com/documentation/development/build-and-test/app-roles", "https://developers.facebook.com/docs/graph-api/guides/explorer/", "https://developers.facebook.com/docs/graph-api/reference/insights"]
---

## TL;DR
"Facebook for Developers" is the gateway to the Graph API. For a hackathon the most useful surface is the **WhatsApp Cloud API test number**. It is free, needs no payment method, and messages up to 5 verified phones, so an agent alert really arrives on a judge's or teammate's phone. Facebook **Pages** posting, comments and insights also work **without App Review** in Development mode, as long as everyone involved has a role on the app. App Review and Business Verification take days and are only needed for outside users. Current API version is **v26.0** (per the facebook-business 26.0.2 SDK, 2026-09-21).

## Request structure
**WhatsApp Cloud API**
- **Send:** `POST /v26.0/{WA_PHONE_NUMBER_ID}/messages` with `Authorization: Bearer $WA_TOKEN` and a JSON body.
  - Template message (always allowed): `{"messaging_product":"whatsapp","to":"1919…","type":"template","template":{"name":"hello_world","language":{"code":"en_US"}}}`.
  - Free text: `{"type":"text","text":{"body":"…"}}`. Only allowed within 24h after the recipient last messaged you.
  - Approve/Reject buttons: `type:"interactive"` with `interactive:{type:"button",…}` (memory).
  - Response: `{messaging_product, contacts:[{input, wa_id}], messages:[{id:"wamid…"}]}` (unverified shape).
- **Webhooks** (configure in the App Dashboard):
  - Verification handshake: `GET` with `hub.mode`, `hub.verify_token`, `hub.challenge`; echo the challenge back.
  - Events: `POST` with `entry[].changes[].value.messages[]` (inbound replies, button clicks) and `.statuses[]` (sent, delivered, read).

**Facebook Pages**
- **Get a Page token:** user token from Graph API Explorer → `GET /me/accounts` returns each Page's `access_token`.
- **Post:** `POST /{page-id}/feed` with `message`, `link`, `published=false` + `scheduled_publish_time`. Returns `{id:"{page-id}_{post-id}"}`.
- **Read comments:** `GET /{post-id}/comments`.
- **Insights:** `GET /{page-id}/insights?metric=page_total_media_view_unique&period=day`.
- **Permissions:** `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`.

**Errors:** `{error:{message, type:"OAuthException", code, error_subcode, fbtrace_id}}`. Code 190 = bad or expired token, 10/200 = permission, 4/17/32 = rate limit (memory).

```bash
curl -s -X POST "https://graph.facebook.com/v26.0/$WA_PHONE_NUMBER_ID/messages" \
  -H "Authorization: Bearer $WA_TOKEN" -H "Content-Type: application/json" \
  -d "{\"messaging_product\":\"whatsapp\",\"to\":\"$WA_TO_NUMBER\",\"type\":\"template\",\"template\":{\"name\":\"hello_world\",\"language\":{\"code\":\"en_US\"}}}"
```
```python
import os, requests
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.page import Page

G = "https://graph.facebook.com/v26.0"
def wa_text(body: str) -> str:     # free text works only inside the 24h window; else send a template
    r = requests.post(f"{G}/{os.environ['WA_PHONE_NUMBER_ID']}/messages", timeout=10,
                      headers={"Authorization": f"Bearer {os.environ['WA_TOKEN']}"},
                      json={"messaging_product": "whatsapp", "to": os.environ["WA_TO_NUMBER"],
                            "type": "text", "text": {"body": body}})
    r.raise_for_status()
    return r.json()["messages"][0]["id"]          # "wamid…"

FacebookAdsApi.init(access_token=os.environ["META_PAGE_TOKEN"])     # SDK defaults to v26.0
post = Page(os.environ["META_PAGE_ID"]).create_feed(params={"message": "Weekly agent report: 0 limit breaches."})
print(post["id"])                                   # "{page-id}_{post-id}"
```

## Simulation & free sandbox
- **WhatsApp test number.** App Dashboard → WhatsApp → API Setup creates a test WABA and a +1 555 test sender.
  - Add up to 5 recipient numbers; each confirms with a code sent in WhatsApp.
  - "Generate access token" gives a temporary token that lasts about 24h. Use a System User token for longer.
  - No payment method is needed to send templates. Messages actually arrive on the phone from "Test Number".
  - You cannot message anyone outside the list, and templates made on the test number can't be reused later.
- **Development mode.** Admins, Developers and Testers can grant themselves any permission without App Review. Queries work on data owned by people with a role on the app, such as Pages you admin. Most apps allow up to 50 testers.
- **Graph API Explorer** (developers.facebook.com/tools/explorer) lets you click to get user/Page tokens and try calls. Good for the first 10 minutes.
- **Test users.** `POST /{app-id}/accounts/test-users` (fields `installed`, `permissions`, `name`) still exists in SDK v26. Whether test users can own Pages in 2026 is unverified.
- **Unpublished Page posts:** `published=false` creates a post that isn't shown on the Page feed, so you can test without spamming followers (memory).

## Visualization ideas
- **WhatsApp-style phone panel:** outbound alerts with tick states driven by webhook `statuses[].status` (sent → delivered → read), and the supervisor's button reply as an inbound bubble.
- **Approval latency chips:** time from `messages[].id` sent to the inbound `interactive.button_reply`, per alert.
- **Page performance line chart** of `page_total_media_view_unique` per day, with markers where the agent published.
- **Comment moderation queue:** `GET /{post-id}/comments` → LLM tags (complaint, scam, praise) → a kanban of agent replies awaiting approval.

## Scenarios (official)
- Business messaging on WhatsApp: notifications, customer support, authentication codes via templates (`/{phone-number-id}/messages`, webhooks).
- Manage a Facebook Page: publish, schedule, moderate comments, read insights (`/{page-id}/feed`, `/{post-id}/comments`, `/{page-id}/insights`).
- Instagram content publishing and insights for professional accounts. Use the Instagram API with Instagram Login; Basic Display was retired in Dec 2024 (memory).
- Ads management and reporting with the Marketing API (`/act_{ad-account-id}/insights`, facebook-business SDK).
- Messenger Platform conversations (`/{page-id}/messages`).

## Finance-agent angle
**Weak-to-moderate fit.** Two honest uses:
1. **WhatsApp as the free human-in-the-loop channel.**
   - The agent wants to exceed a limit, so it sends an alert with Approve/Reject buttons. The webhook records the decision.
   - This dodges Twilio's US-SMS trial blocks.
   - First message the test number from the supervisor's phone to open the 24h free-text window (that a verified recipient can reply is unverified). Otherwise send `hello_world` as the attention ping.
2. **Social customer-care agent for a bank's Page.** It triages comments (fraud/scam reports, complaints) and drafts replies that a human approves. The dashboard shows queue size and SLA.

Neither uses Meta data as a market signal.

## Gotchas
- **Account checkpoints.** Brand-new Facebook accounts often get checkpointed when they create apps or Pages (memory). Use an established account; the developer account also needs phone verification.
- **Development mode is role-only.** Anyone without an app role (a judge's own Facebook account) needs Advanced Access, which means App Review plus Business Verification. Not possible this weekend; demo with team accounts.
- **Token lifetimes:**
  - Explorer user tokens last about 1–2h (memory). Swap for a long-lived token with `GET /oauth/access_token?grant_type=fb_exchange_token`.
  - The WhatsApp temporary token lasts about 24h. Regenerate it on Sunday morning or use a System User token.
- **WhatsApp rules:**
  - Business-initiated messages must be templates. `hello_world` is pre-approved; custom templates need review (minutes to hours, unverified).
  - Phone numbers go without `+` in `to` (memory).
- **Page Insights metric removals.** Many legacy impression and reach metrics were removed on 2026-06-15 for all API versions; they now return an invalid-metric error. Use `page_total_media_view_unique` and the other media-view metrics. Old tutorials using `page_impressions*` will fail.
- **Version pinning.** Put `v26.0` in every URL. Versions expire about 2 years after release (memory); v25.0 shipped 2026-02-18.
- **Webhooks** need public HTTPS (cloudflared/ngrok) and a matching `WA_VERIFY_TOKEN`.

## Mock fallback
- **Adapter:** `META_MODE=mock|live` behind the same `Notifier` interface as `twilio`: `send_alert(text) -> id`, `request_approval(req_id, summary)`.
- **Mock sends:** return `wamid.mock-<n>`, then emit fake `statuses` events (sent → delivered → read over about 3 s) on the dashboard SSE bus.
- **Mock approvals:** an on-screen "phone" with Approve/Reject buttons POSTs a payload shaped like the real webhook (`entry[0].changes[0].value.messages[0].interactive.button_reply`) to your own `/meta/webhook`.
- **Pages mock:** posts go to `fixtures/meta_outbox.json` with ids `{page}_{n}`. Insights come from a seeded generator (daily values with a bump after each post). A replay script can also POST captured real webhook JSON to localhost.

## Sources
- https://pypi.org/project/facebook-business/26.0.2/ (sdk-source: API_VERSION v26.0, Page.create_feed/get_insights/create_message, Application test-users endpoint and fields, WhatsApp business account objects)
- https://registry.npmjs.org/facebook-nodejs-business-sdk/latest (sdk-source: 24.0.1)
- https://developers.facebook.com/documentation/business-messaging/whatsapp/get-started (search-snippet: temporary token, up to 5 recipients, hello_world, phone-number-id path)
- https://developers.facebook.com/documentation/business-messaging/whatsapp/about-the-platform (search-snippet: test WABAs need no payment method for templates)
- https://developers.facebook.com/docs/graph-api/guides/explorer/ and https://developers.facebook.com/documentation/development/build-and-test/app-roles (search-snippet: dev-mode permissions for role holders, App Review for live, roles, 50 testers)
- https://developers.facebook.com/docs/graph-api/reference/insights and https://developers.facebook.com/blog/post/2026/02/18/introducing-graph-api-v25-and-marketing-api-v25 (search-snippet: metric deprecation 2026-06-15, media views replacement)
- https://improvado.io/product-updates/connectors/facebook-pages-metrics-deprecation (search-snippet, third-party: page_impressions_unique → page_total_media_view_unique)
- https://help.seven.io/en/whatsapp/whatsapp-meta-test-number (search-snippet, third-party: +1 555 test number, not billed)
- Error codes, token lifetimes, interactive buttons, checkpoint risk, Basic Display retirement (memory)

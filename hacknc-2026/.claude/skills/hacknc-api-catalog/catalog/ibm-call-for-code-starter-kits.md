---
# ---- identity -------------------------------------------------------------
id: ibm-call-for-code-starter-kits
name: IBM Call for Code COVID-19 Solution Starter Kits (2020)
provider: IBM / Call for Code
category: starter-kit
source: resources-doc
listed_as: "COVID-19 Cooperation/Communication/Education Starter Kit"
# ---- availability ---------------------------------------------------------
status: legacy
cost_model: free
free_allowance: "Repos Apache-2.0; IBM watsonx Assistant Lite ~1,000 MAU / 10,000 msgs per month (unverified); Cloudant Lite tier"
card_required: unknown
signup_minutes: 30
auth: "IBM Cloud IAM API key per service (IamAuthenticator); HERE API key for maps"
base_url: "https://api.us-south.assistant.watson.cloud.ibm.com (Assistant, region-specific; kit default gateway.watsonplatform.net is retired)"
env_vars: [ASSISTANT_URL, ASSISTANT_ID, ASSISTANT_IAM_APIKEY, CLOUDANT_ID, CLOUDANT_IAM_APIKEY, HERE_APIKEY, STARTER_KIT_SERVER_URL]
sdks: ["node: ibm-watson@12.2.0 (kit pins ^5.4.0)", "node: @ibm-cloud/cloudant@0.12.25 (kit uses deprecated @cloudant/cloudant ^4.2.4)"]
# ---- simulation -----------------------------------------------------------
sandbox: "none; Watson Assistant 'Preview link' for manual testing only"
offline_mock: easy
# ---- fit for builders -----------------------------------------------------
demo_effect: 1
integration_hours: "4-8"
risk: high
track_fit: [hacknc-community]
finance_fit: 1
tags: [starter-kit, legacy, chatbot, watson, react-native, covid, archived]
# ---- provenance -----------------------------------------------------------
verified: search-snippet
last_checked: 2026-10-10
docs: ["https://github.com/Call-for-Code/Solution-Starter-Kit-Cooperation-2020", "https://github.com/Call-for-Code/Solution-Starter-Kit-Communication-2020", "https://github.com/Call-for-Code/Solution-Starter-Kit-Education-2020"]
---

## TL;DR
These are three IBM Call for Code starter repos from 2020. All three are **archived** (read-only, default branch `master`, Apache-2.0). They are COVID-era templates built on IBM Watson services, several of which are now retired or renamed. Don't build on them. What's still worth taking is the **architecture patterns**: a chat proxy, resource CRUD, a webhook into the assistant, and a Slack/voice channel. Rebuild those patterns with a current LLM API. Fit for a finance-agent project is weak.

## Request structure
**How to run a kit** (Cooperation, per its README). This is not recommended in 2026:
```bash
git clone --depth 1 https://github.com/Call-for-Code/Solution-Starter-Kit-Cooperation-2020 && cd Solution-Starter-Kit-Cooperation-2020
cd starter-kit/server-app && cp .env.example .env    # ASSISTANT_URL/ID/IAM_APIKEY, CLOUDANT_ID/IAM_APIKEY
npm install && npm start                             # Express on http://localhost:3000
cd ../mobile-app && cp .env.example .env             # STARTER_KIT_SERVER_URL, HERE_APIKEY
npm install && npm run ios                           # React Native 0.62.3 / React 16.9 (2020 toolchain)
```
The server API is still a useful shape to copy (from `server.js`):
- `GET /api/session`: creates an Assistant v2 session and returns the session id.
- `POST /api/message {text, sessionid}`: sends to Assistant, then post-processes. If the intent asks for supplies, it looks up matching resources in Cloudant.
- `GET /api/resource?type=&name=&userID=` and `POST /api/resource {type: Food|Other|Help, name, contact, userID, description?, quantity?, location?}`, plus `PATCH`/`DELETE /api/resource/:id`.

**What each kit is:**
| kit | idea | stack |
|---|---|---|
| Cooperation | suppliers post goods; recipients ask a chatbot and get a map route | Watson Assistant, Cloudant, HERE maps/routing, Node/Express, React Native |
| Communication | COVID FAQ chatbot with news and stats; web, Slack, Node-RED voice, WhatsApp | Watson Assistant + Discovery, Cloud Functions (OpenWhisk), STT/TTS, covid19api.com |
| Education | quiz app; video transcription and translation | LoopBack/Express + React, Watson STT, Language Translator, Object Storage, Cloud Foundry/Kubernetes |

## Simulation & free sandbox
There's no built-in sandbox. The only test path in the kits is Watson Assistant's **Preview link**. To work offline, swap the Assistant call for a stub (see Mock fallback). The kits import dialog-skill JSON files (`starter-kit-cooperation-dialog-skill.json`, `skill-CDC-COVID-FAQ.json`). Those files list intents, examples, and answers, and they're still readable as seed data for an intent classifier or an LLM few-shot prompt.

## Visualization ideas
- **Supply/need map** (Cooperation): `resource.location` pins colored by `type` (Food/Other/Help), with the route to the nearest match.
- **Chat transcript with intent chips:** each turn shows the detected intent, the backend call made (`/api/resource` query), and the result count.
- **Channel fan-out diagram** (Communication): one assistant serving web, Slack, voice, and WhatsApp.

## Scenarios (official)
- **Cooperation:** community cooperation in a crisis, letting suppliers advertise stock and recipients find it through chat and get routed there (`/api/message` plus `/api/resource`).
- **Communication:** answer high volumes of crisis questions with a chatbot, keep information consistent, and dynamically fetch news and statistics through webhooks (Assistant webhook to Cloud Functions to Discovery or a stats API).
- **Education:** keep remote learning going with a quiz app, a video transcriber/translator, and a Skills Network virtual classroom.

## Finance-agent angle
The direct fit is weak. The only part that transfers is the pattern: a thin server that proxies chat, detects intent, then calls a domain API and enriches the reply (Cooperation's `post_process_assistant`). That maps onto "agent decides, then calls the account or transactions API, and the monitor logs the call". Write that layer fresh against a current LLM with tool calling, not Watson.

## Gotchas
- All three repos are **archived**: Cooperation last pushed 2022-04, Communication 2021-10, Education 2020-03. Use `master`, since `main` returns 404.
- Retired or changed IBM pieces:
  - Watson Language Translator was withdrawn on 2024-12-10 (search-snippet), so the Education translation path is dead.
  - IBM Cloud Foundry (`ibmcloud app push`, `*.bluemix.net` URLs) has been deprecated since 2023 (unverified).
  - Watson Assistant was rebranded watsonx Assistant (unverified whether new Lite instances are still offered in 2026).
  - Watson Voice Agent is discontinued (unverified).
- The kit's default `ASSISTANT_URL` is `gateway.watsonplatform.net` (retired, unverified). Set the regional `api.<region>.assistant.watson.cloud.ibm.com` instead.
- Dependency rot: `@cloudant/cloudant` is deprecated on npm (replace it with `@ibm-cloud/cloudant`). `ibm-watson` jumped from ^5 to 12.x. React Native 0.62 won't build on current Xcode/Android SDKs (unverified).
- `covid19api.com` (the Communication stats source) is shut down (unverified). The HERE "Freemium" plan link is from 2020, and the current HERE plans are different (unverified).
- IBM Cloud signup may ask for card or identity verification (unverified), so allow 30+ minutes.
- Devpost rule: no pre-written code. A cloned archived kit counts as third-party code. Credit it, and don't present it as your own work.

## Mock fallback
Replace `lib/assistant.js` with a stub that keeps the same `session()`/`message(text, sessionid)` signatures. Keyword-match the intents in the imported dialog-skill JSON and return the same response shape. Back `/api/resource` with an in-memory array or SQLite. Select the stub with `ASSISTANT_MODE=fixture`.

## Sources
- https://raw.githubusercontent.com/Call-for-Code/Solution-Starter-Kit-{Cooperation,Communication,Education}-2020/master/README.md (official-docs)
- Cooperation `starter-kit/server-app/{package.json,server.js,lib/assistant.js}` and `mobile-app/package.json` (official-docs)
- GitHub search org:Call-for-Code: archived=true, pushed_at, license Apache-2.0 (official-docs)
- registry.npmjs.org: ibm-watson 12.2.0, @ibm-cloud/cloudant 0.12.25, @cloudant/cloudant deprecated (sdk-source)
- IBM Language Translator deprecation timeline; watsonx Assistant Lite limits (search-snippet)
- Cloud Foundry deprecation, covid19api shutdown, gateway.watsonplatform.net retirement (memory)

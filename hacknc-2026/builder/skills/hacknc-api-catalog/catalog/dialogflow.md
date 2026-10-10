---
# ---- identity -------------------------------------------------------------
id: dialogflow
name: Google Dialogflow (ES and CX / Conversational Agents)
provider: Google Cloud
category: conversational
source: resources-doc
listed_as: "Google Dialogflow (Text/Voice Interfaces)"
# ---- availability ---------------------------------------------------------
status: changed
cost_model: free-tier
free_allowance: "ES Trial edition: text free (180 req/min), audio 1,000/day & 15,000/month; CX: $600 flow credit + $1,000 generative credit for 12 months (needs a billing account)"
card_required: true
signup_minutes: 25
auth: "Authorization: Bearer <OAuth2 token> from a service account (GOOGLE_APPLICATION_CREDENTIALS) or ADC; role roles/dialogflow.client"
base_url: "https://dialogflow.googleapis.com/v2 (ES) | https://{location}-dialogflow.googleapis.com/v3 (CX)"
env_vars: [GOOGLE_APPLICATION_CREDENTIALS, DIALOGFLOW_PROJECT_ID, DIALOGFLOW_LOCATION, DIALOGFLOW_AGENT_ID]
sdks: ["python: google-cloud-dialogflow==2.53.0", "python: google-cloud-dialogflow-cx==2.9.0", "node: @google-cloud/dialogflow@8.3.0", "node: @google-cloud/dialogflow-cx@6.3.0"]
# ---- simulation -----------------------------------------------------------
sandbox: "ES Trial edition is free and rate-limited; both consoles have a built-in simulator that shows the raw JSON. No fake-credential mode"
offline_mock: easy
# ---- fit for builders -----------------------------------------------------
demo_effect: 3
integration_hours: "2-4"
risk: medium
track_fit: [hacknc-general, hacknc-beginner]
finance_fit: 2
tags: [chatbot, voice, intents, conversational, agent-builder, google-cloud]
# ---- provenance -----------------------------------------------------------
verified: search-snippet
last_checked: 2026-10-10
docs: ["https://cloud.google.com/dialogflow/docs/quick", "https://cloud.google.com/dialogflow/es/docs", "https://cloud.google.com/dialogflow/cx/docs", "https://cloud.google.com/dialogflow/quotas", "https://cloud.google.com/products/dialogflow-es/pricing"]
---

## TL;DR
Dialogflow is Google's intent and flow chatbot engine. It comes in two editions with separate APIs and SDKs.
- **ES** (`v2`) is the older, simpler intents-and-contexts product. Its **Trial edition is free**, with rate limits.
- **CX** (`v3`) uses flows, pages and generative "playbooks". On 31 Oct 2025 its console was folded into the **Conversational Agents** console, which also absorbed Vertex AI Agent Builder. The API is unchanged. CX needs billing but comes with $600 + $1,000 trial credits.

For a quick text or voice front-end, use ES. Use CX only if you want Gemini-backed playbooks or execution traces.

## Request structure
Both editions use the same call: `POST .../sessions/{SESSION_ID}:detectIntent`. Reuse the same session ID to continue a conversation.
- **ES**: `https://dialogflow.googleapis.com/v2/projects/{project}/agent/sessions/{sid}:detectIntent`. There is one agent per project, and `languageCode` goes inside `text`.
- **CX**: `https://{loc}-dialogflow.googleapis.com/v3/projects/{p}/locations/{loc}/agents/{agent}/sessions/{sid}:detectIntent`. The `global` location uses `dialogflow.googleapis.com` instead. `languageCode` sits at the `queryInput` level. Add `"responseView":"DETECT_INTENT_RESPONSE_VIEW_FULL"` to get `traceBlocks`.
```bash
# token: SA key via GOOGLE_APPLICATION_CREDENTIALS, or `gcloud auth application-default login`
TOKEN=$(gcloud auth application-default print-access-token)
curl -s -X POST \
  "https://dialogflow.googleapis.com/v2/projects/$DIALOGFLOW_PROJECT_ID/agent/sessions/demo-001:detectIntent" \
  -H "Authorization: Bearer $TOKEN" -H "x-goog-user-project: $DIALOGFLOW_PROJECT_ID" \
  -H "Content-Type: application/json" \
  -d '{"queryInput":{"text":{"text":"What is my checking balance?","languageCode":"en-US"}}}'
# CX body: {"queryInput":{"text":{"text":"..."},"languageCode":"en"},
#           "queryParams":{"analyzeQueryTextSentiment":true},"responseView":"DETECT_INTENT_RESPONSE_VIEW_FULL"}
```
ES response, with field names from the v2 `QueryResult` proto:
`{"responseId":"...","queryResult":{"queryText":"...","action":"balance.check","parameters":{"account":"checking"},"allRequiredParamsPresent":true,"fulfillmentText":"Your balance is ...","intent":{"name":"projects/.../intents/<id>","displayName":"balance.check"},"intentDetectionConfidence":0.87,"languageCode":"en-us"}}`.

The CX `queryResult` has these fields:
- `text`
- `parameters`
- `responseMessages[].text.text[]`
- `currentPage.displayName`
- `currentFlow`
- `intent`
- `match{matchType,confidence}`
- `sentimentAnalysisResult`
- `traceBlocks[]`, which has `actions[]` (userUtterance / agentUtterance / toolUse / playbookInvocation), `startTime`, `completeTime` and `endState`.
```python
import os, uuid
from google.cloud import dialogflow            # ES; CX: from google.cloud import dialogflowcx_v3

client = dialogflow.SessionsClient()            # reads GOOGLE_APPLICATION_CREDENTIALS / ADC
session = client.session_path(os.environ["DIALOGFLOW_PROJECT_ID"], str(uuid.uuid4()))
resp = client.detect_intent(request={"session": session, "query_input": {
    "text": {"text": "Freeze my debit card", "language_code": "en-US"}}})
qr = resp.query_result
print(qr.intent.display_name, round(qr.intent_detection_confidence, 2), qr.fulfillment_text, dict(qr.parameters))
# CX: dialogflowcx_v3.SessionsClient(client_options={"api_endpoint": f"{loc}-dialogflow.googleapis.com"})
```

## Simulation & free sandbox
- **ES Trial edition**: no charge. Text runs at 180 req/min. Audio is 100/min, 1,000/day and 15,000/month, with a 60 s cap per request. Essentials edition text costs $0.002/request.
- **CX**: $600 credit for flows and $1,000 for generative features, both valid 12 months. They activate on first use and need a billing account.
- The **console simulator** ("Try it now" in ES, "Test agent" in CX) shows the matched intent, parameters, page transitions and raw response JSON, with no code. **Dialogflow Messenger** is an embeddable web-chat widget that gives you a chat UI in one `<df-messenger>` tag.
- **Prebuilt content**: CX has prebuilt financial-services components (account balance, make a payment, lock card, disputes, transaction history) and prebuilt agents (English only). ES has a prebuilt banking agent tutorial.

## Visualization ideas
- **Intent-confidence bar per turn**: `intent.displayName` with `intentDetectionConfidence` (ES) or `match.confidence` (CX), with a red outline below 0.5 for fallback.
- **Conversation state graph**: CX `currentFlow` → `currentPage.displayName` as nodes, with one edge per turn. This shows where users get stuck.
- **Agent trace swimlane**: CX `traceBlocks[].actions` (userUtterance, toolUse with input/output params, agentUtterance) on a time axis from `startTime`/`completeTime`, colored by `endState`.
- **Sentiment line**: `sentimentAnalysisResult.score` per user turn (CX `analyzeQueryTextSentiment` / ES sentiment config).

## Scenarios (official)
- Customer-service virtual agents on web/app chat, via `detectIntent` and Dialogflow Messenger.
- Voice IVR / phone bots, via audio `detectIntent`, `streamingDetectIntent` and telephony integrations (CX Phone Gateway, CCAI).
- Banking self-service (balance, payments, card lock, disputes, transactions), via CX prebuilt components, with flexible webhooks pointing to your backend.
- Generative FAQ/RAG agents (data store agents, playbooks on Gemini), via CX `detectIntent` with playbooks. New playbooks default to `gemini-2.5-flash`.

## Finance-agent angle
Weak-to-moderate fit when Claude is the brain, because Dialogflow duplicates its language understanding. There are two honest uses:
1. **Deterministic compliance front door.** Regulated intents (lock card, dispute, payment) run fixed, auditable flows, and everything else falls through by webhook to the Claude agent. The demo story is "an LLM never improvises a dispute flow".
2. **Monitored second agent.** CX `traceBlocks` (FULL view) supply tool-call and timing data to drive the monitoring dashboard alongside Claude's traces.

It does not help with market data or analytics.

## Gotchas
- **ES vs CX mix-ups**: the SDKs differ (`google.cloud.dialogflow` vs `google.cloud.dialogflowcx_v3`), as do the API versions (`v2` vs `v3`), the resource paths (`agent` singular vs `locations/*/agents/*`) and where `languageCode` goes.
- **CX regional endpoint**: a non-`global` agent must be called on `{loc}-dialogflow.googleapis.com`. Otherwise you get 400 or not-found errors.
- **`traceBlocks` are omitted** unless `responseView=DETECT_INTENT_RESPONSE_VIEW_FULL`. The BASIC view also drops `diagnosticInfo`.
- **Billing**: CX and the GCP $300 free trial need a billing account, which means a card. ES Trial edition may work without one (unverified).
- **Service-account keys** may be blocked by org policy on school-managed Google accounts. Use a personal Gmail project, or ADC plus the `x-goog-user-project` header.
- **Console rename**: tutorials say "Dialogflow CX console". It is now the Conversational Agents console, and agents carry over.
- **Audio quotas** on the ES trial are small: 1,000/day. Sessions expire after ~30 min idle (unverified). Webhooks time out in ~5 s by default (unverified).
- Dialogflow **V1 API** code and `dialogflow` npm/pip packages from before 2020 are obsolete.

## Mock fallback
Use one interface: `detect(text, session_id) -> {intent, confidence, params, reply, page}`. With `DIALOGFLOW_MODE=mock` (or `DEMO_MODE=1`), a keyword/regex table in `fixtures/dialogflow_intents.json` handles it. Example rules: `balance|how much` → `balance.check`, and `freeze|lock` → `card.lock` with confidence 0.9. Anything else goes to `fallback` at 0.3, which then calls Claude. Commit an ES agent export ZIP or a CX agent export to the repo so the agent can be restored to a fresh project in minutes.

## Sources
- https://pypi.org/project/google-cloud-dialogflow/ (wheel 2.53.0: `dialogflow_v2/types/session.py`, REST transport URIs) (sdk-source)
- https://pypi.org/project/google-cloud-dialogflow-cx/ (wheel 2.9.0: `types/session.py`, `types/trace.py`, `DetectIntentResponseView`, README "Enable billing") (sdk-source)
- https://raw.githubusercontent.com/GoogleCloudPlatform/python-docs-samples/main/dialogflow/detect_intent_texts.py (sdk-source)
- https://raw.githubusercontent.com/GoogleCloudPlatform/python-docs-samples/main/dialogflow-cx/detect_intent_texts.py (sdk-source)
- https://docs.cloud.google.com/dialogflow/quotas (Trial quotas) (search-snippet)
- https://cloud.google.com/products/dialogflow-es/pricing and https://cloud.google.com/dialogflow/pricing (ES $0.002, CX $600/$1,000 credits) (search-snippet)
- https://docs.cloud.google.com/dialogflow/docs/release-notes (CX console deprecated 31 Oct 2025; playbook default model) (search-snippet)
- https://docs.cloud.google.com/dialogflow/cx/docs/concept/prebuilt-component (financial-services components) (search-snippet)

---
# ---- identity -------------------------------------------------------------
id: ibm-watson
name: IBM Watson / watsonx.ai (Granite LLMs, NLU, Speech, Assistant)
provider: IBM
category: ml-nlp
source: resources-doc
listed_as: "IBM Watson"
# ---- availability ---------------------------------------------------------
status: changed
cost_model: free-tier
free_allowance: "watsonx.ai Runtime Lite: 300,000 tokens + 20 CUH/month; Lite plans for NLU, STT (500 min/mo), TTS, watsonx Assistant; IBM Cloud signup puts a card on file"
card_required: true
signup_minutes: 30
auth: "IAM: POST https://iam.cloud.ibm.com/identity/token (grant_type=urn:ibm:params:oauth:grant-type:apikey) -> Authorization: Bearer <token>, ~60 min TTL"
base_url: "https://us-south.ml.cloud.ibm.com/ml/v1"
env_vars: [IBM_CLOUD_API_KEY, WATSONX_PROJECT_ID, WATSONX_URL, NLU_URL]
sdks: ["python: ibm-watsonx-ai==1.8.0", "python: ibm-watson==11.2.0", "node: @ibm-cloud/watsonx-ai@1.7.16", "node: ibm-watson@12.2.0"]
# ---- simulation -----------------------------------------------------------
sandbox: "No test mode. Lite plans are the free tier: real calls, monthly caps, no charges. Prompt Lab in the browser for trying prompts with no code"
offline_mock: easy
# ---- fit for builders -----------------------------------------------------
demo_effect: 2
integration_hours: "2-4"
risk: medium
track_fit: [hacknc-general]
finance_fit: 3
tags: [llm, granite, guardrails, sentiment, nlp, speech, ibm]
# ---- provenance -----------------------------------------------------------
verified: search-snippet
last_checked: 2026-10-10
docs: ["https://www.ibm.com/watson/developer-resources/", "https://cloud.ibm.com/apidocs/watsonx-ai", "https://ibm.github.io/watsonx-ai-python-sdk/", "https://cloud.ibm.com/apidocs/natural-language-understanding", "https://github.com/watson-developer-cloud/python-sdk"]
---

## TL;DR
In 2026 "IBM Watson" means two things. The main one is **watsonx.ai**, IBM's foundation-model platform: Granite and third-party LLMs, chat, embeddings and guardrail detection, all behind one IAM-authenticated REST API. The other is the few **classic Watson services** still offered: NLU, Speech to Text, Text to Speech and watsonx Assistant. Each has a free Lite plan. Know first that an IBM Cloud account needs a card for identity verification. Also, the watsonx project has to be linked to a watsonx.ai Runtime instance before any API call works.

## Request structure
**watsonx.ai chat** (paths from the `ibm-watsonx-ai` 1.8.0 source): `POST {WATSONX_URL}/ml/v1/text/chat?version=YYYY-MM-DD`, where the SDK sends `2026-09-25`. Body: `model_id`, `project_id`, `messages` (OpenAI-style roles), and optional `max_tokens`, `temperature`, `tools`, `tool_choice_option`. The answer is in `choices[0].message.content`. `usage.{prompt,completion,total}_tokens` is also returned (unverified).
```bash
export WATSONX_URL=${WATSONX_URL:-https://us-south.ml.cloud.ibm.com}
TOKEN=$(curl -s -X POST https://iam.cloud.ibm.com/identity/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=$IBM_CLOUD_API_KEY" | jq -r .access_token)
curl -s "$WATSONX_URL/ml/v1/text/chat?version=2026-09-25" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"model_id":"ibm/granite-4-h-small","project_id":"'"$WATSONX_PROJECT_ID"'",
       "messages":[{"role":"system","content":"You audit trading-agent actions."},
                   {"role":"user","content":"Agent bought 3x leveraged ETF with 80% of cash. Risky? One line."}],
       "max_tokens":120,"temperature":0}' | jq -r '.choices[0].message.content'
```
```python
import os
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

model = ModelInference(
    model_id="ibm/granite-4-h-small",
    credentials=Credentials(url=os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
                            api_key=os.environ["IBM_CLOUD_API_KEY"]),
    project_id=os.environ["WATSONX_PROJECT_ID"])
r = model.chat(messages=[{"role": "user", "content": "Summarize: AAPL beat EPS by 4%."}],
               params={"max_tokens": 120, "temperature": 0})
print(r["choices"][0]["message"]["content"])
```
Other endpoints (paths from SDK source):
- `POST /ml/v1/text/detection` with `{input, project_id, detectors:{granite_guardian:{threshold:0.4}, hap:{threshold:0.4}, pii:{}}}` runs guardrails on any text (the SDK `Guardian` class).
- `POST /ml/v1/text/generation` (prompt in, `results[0].generated_text` out), `/text/chat_stream` (SSE), `/text/embeddings`.
- `GET /ml/v1/foundation_model_specs?version=...&filters=function_text_chat,!lifecycle_withdrawn:and` lists the models live in your region.
- **NLU**: `POST {NLU_URL}/v1/analyze?version=2022-04-07` with body `{"text":..., "features":{"sentiment":{}, "entities":{"sentiment":true}, "keywords":{}}}`. Python: `NaturalLanguageUnderstandingV1(version=..., authenticator=IAMAuthenticator(key))`, then `.set_service_url(NLU_URL)`. The default URL is `https://api.us-south.natural-language-understanding.watson.cloud.ibm.com`.

**Service status, 2026**
| Service | Status | Free (Lite) |
|---|---|---|
| watsonx.ai Runtime (Granite, Llama, Mistral...) | active | 300k tokens + 20 CUH/month |
| Natural Language Understanding | active (still in SDK 11.2.0, Jan 2026) | ~30k NLU items/month (unverified) |
| Speech to Text / Text to Speech | active | STT 500 min/month; TTS ~10k chars/month (unverified) |
| watsonx Assistant (was Watson Assistant) | active, v2 API | ~1,000 MAU (unverified) |
| Discovery | v1 removed (end of support 11 Jul 2023); v2 still in SDK, but no Lite plan confirmed | treat as paid |
| Language Translator | withdrawn 10 Dec 2024; removed in SDK 9.0.0 | none |
| Tone Analyzer, Personality Insights, Visual Recognition, NL Classifier, Compare & Comply | retired 2021-2023; removed in SDK 6.0.0 | none |

## Simulation & free sandbox
- There are no fake credentials. The Lite plans are the sandbox: real responses, capped, and never billed unless you upgrade.
- watsonx.ai **Prompt Lab** (browser) runs Granite against your project and has a "view code" option that exports curl/Python (unverified). A separate 30-day watsonx demo with 20k tokens takes an IBM, Google or LinkedIn login, but it is UI only.
- Output shapes:
  - Chat returns `{"model_id":"ibm/granite-4-h-small","choices":[{"message":{"role":"assistant","content":"High risk: ..."},"finish_reason":"stop"}]}`.
  - NLU returns `{"sentiment":{"document":{"score":-0.71,"label":"negative"}},"entities":[{"type":"Company","text":"Apple","relevance":0.98,"sentiment":{...}}]}`.
  - Detection returns a `detections` list with type, span and score (field names unverified).

## Visualization ideas
- **Guardrail chips per agent message**: for each Claude agent output, show HAP/PII/Granite-Guardian badges colored by `detections[].score`.
- **News-sentiment heat strip**: tickers × time, colored by NLU `sentiment.document.score`, with the `entities[]` count per cell.
- **Entity graph**: nodes from NLU `entities` and edges from `relations`, to show which companies co-occur in a news feed.
- **Lite budget meter**: token gauge against the 300k/month cap, driven by `usage.total_tokens`.

## Scenarios (official)
- Generation, summarization, classification, extraction and RAG with Granite and other models, via `/ml/v1/text/chat` and `/text/generation`.
- Granite Guardian risk detection (harm, jailbreak, groundedness/hallucination in RAG), via `/ml/v1/text/detection` or the `ibm/granite-guardian-*` models (model IDs unverified).
- Text analytics (sentiment, emotion, entities, keywords, categories), via NLU `/v1/analyze`.
- Contact-center transcription and voice bots, via STT `/v1/recognize` and TTS `/v1/synthesize`.
- Customer-service virtual agents, via watsonx Assistant v2 `message`. This now needs an `environment_id`.

## Finance-agent angle
Moderate fit, as a **second-vendor monitor** rather than the brain. Claude stays the agent. Every proposed action or reply passes through `/text/detection` (granite_guardian + pii) and is shown on the monitoring dashboard. "An independent IBM model audits each agent step" is easy to pitch, and IBM is a familiar name in banking AI governance. watsonx.governance markets agent monitoring directly, but no Lite plan is confirmed for it (unverified). NLU sentiment on headlines can be a market-context feed for the agent. As a primary LLM, Granite is not better than Claude, so don't swap it in.

## Gotchas
- **Card on file**: IBM's free-account page says payment details are required (a verification hold). Lite services never charge, but don't upgrade to Pay-As-You-Go by accident.
- **Project ↔ Runtime association**: a new watsonx project must have a watsonx.ai Runtime service associated (Project → Manage → Services & integrations). Without it, calls fail with an auth/instance error (exact message unverified).
- **Region must match**: `WATSONX_URL` must be the region of your Runtime instance (`us-south`, `eu-de`, `eu-gb`, `jp-tok`, `au-syd`, ...).
- **Every REST call needs `?version=YYYY-MM-DD`**. IAM tokens expire after ~1 h; the SDKs refresh them, curl scripts do not.
- **Model churn**: `ibm/granite-3-3-8b-instruct` reportedly returns 404 `model_not_supported` now. Call `foundation_model_specs` first and keep `model_id` in config.
- **Lite limits**: one Lite instance per service per account. Lite instances are deleted after 30 days of inactivity. Lite reportedly allows ~2 req/s (unverified).
- **Old tutorials are dead**: the `watson-developer-cloud` package, `gateway.watsonplatform.net` URLs, `iam_apikey=` args, and Discovery v1 / Translator / Tone Analyzer code.
- The NLU `emotion` feature is English-only (unverified).

## Mock fallback
Put two functions behind one interface: `risk_check(text) -> {flags:[{type,score}], max_score}` and `sentiment(text) -> {score,label}`. `IBM_MODE=live` calls IBM and saves each response to `fixtures/ibm/<sha1(input)>.json`. `IBM_MODE=cache` (or `DEMO_MODE=1`) serves those fixtures instead. If there is no fixture, fall back to keyword rules: leverage/margin/"all-in" → high risk, and regexes for SSNs and account numbers → pii.

Granite models are open-weight (Apache-2.0), so a local Granite or Granite Guardian through Ollama or Hugging Face can stand in offline. Availability and laptop fit are unverified.

## Sources
- https://pypi.org/project/ibm-watsonx-ai/ (wheel 1.8.0: `href_definitions.py`, `model_inference.py`, `moderations/guardian.py`, `utils/API_VERSION_PARAM`) (sdk-source)
- https://pypi.org/project/ibm-watson/ (sdist 11.2.0: README, NLU/STT/TTS/Assistant/Discovery v2 modules) (sdk-source)
- https://raw.githubusercontent.com/watson-developer-cloud/python-sdk/master/CHANGELOG.md (removals in 6.0.0 and 9.0.0) (sdk-source)
- https://www.ibm.com/products/watsonx-ai/pricing and https://dataplatform.cloud.ibm.com/docs/content/wsj/getting-started/wml-plans.html (Lite 300k tokens / 20 CUH) (search-snippet)
- https://www.ibm.com/products/cloud/free (card required, Lite never charges) (search-snippet)
- https://cloud.ibm.com/catalog/services/speech_to_text (500 min, 30-day inactivity deletion) (search-snippet)
- https://community.ibm.com/community/user/question/any-ibm-alternatives-of-ibm-language-translator-that-is-being-deprecated-after-10-december-2024 (Translator withdrawal) (search-snippet)
- https://github.com/spring-ai-community/spring-ai-watsonx-ai/issues/212 (granite-4-h-small works; 3-3-8b 404) (search-snippet)
- https://www.ibm.com/products/watsonx/get-started (30-day trial / demo) (search-snippet)

---
# ---- identity -------------------------------------------------------------
id: gemini-api
name: Google Gemini API (AI Studio key, google-genai SDK)
provider: Google
category: llm
source: tracks-page
listed_as: "[MLH] Best Use of Gemini API"
# ---- availability ---------------------------------------------------------
status: active
cost_model: free-tier
free_allowance: "Free tier on Flash / Flash-Lite models, no card. Per-model RPM/RPD shown only in AI Studio (3rd-party guides: ~10 RPM and 250-1,500 RPD for Flash, unverified). Pro needs billing"
card_required: false
signup_minutes: 3
auth: "Header x-goog-api-key: <key> (key from aistudio.google.com/apikey)"
base_url: "https://generativelanguage.googleapis.com/v1beta"
env_vars: [GEMINI_API_KEY, GEMINI_MODEL]
sdks: ["python: google-genai==2.29.0", "node: @google/genai@2.28.0"]
# ---- simulation -----------------------------------------------------------
sandbox: "Free tier is the sandbox (real calls, rate-limited; Google may use free-tier prompts to improve its products). AI Studio playground exports curl/Python"
offline_mock: easy
# ---- fit for builders -----------------------------------------------------
demo_effect: 4
integration_hours: "1-2"
risk: low
track_fit: [mlh-gemini, hacknc-general, sponsor-finance]
finance_fit: 4
tags: [llm, multimodal, pdf, vision, function-calling, structured-output, second-opinion, mlh]
# ---- provenance -----------------------------------------------------------
verified: search-snippet
last_checked: 2026-10-10
docs: ["https://ai.google.dev/gemini-api/docs", "https://ai.google.dev/gemini-api/docs/changelog", "https://ai.google.dev/gemini-api/docs/rate-limits", "https://github.com/googleapis/python-genai", "https://googleapis.github.io/python-genai/"]
---

## TL;DR
The Gemini API is Google's multimodal LLM API. It takes text, images, PDFs, audio and video in one `generateContent` call, and supports function calling and JSON-schema output. You get a key from Google AI Studio in about 2 minutes, with no card, and Flash / Flash-Lite are free with rate limits. Two things to know first:
- **Model IDs churn monthly.** On 8 Oct 2026, 3.5→3.6 and 3.7→3.8 Flash were auto-rerouted. Read the model from `GEMINI_MODEL` and default to the `gemini-flash-latest` alias.
- **Use the `google-genai` SDK** (`from google import genai`), not the legacy `google-generativeai`.

## Request structure
`POST {base}/models/{model}:generateContent`, with `streamGenerateContent?alt=sse` for streaming.
- **Request body**: `contents[{role:"user"|"model", parts:[{text}|{inlineData:{mimeType,data(base64)}}|{functionCall}|{functionResponse}]}]`, plus optional `systemInstruction`, `tools[{functionDeclarations:[{name,description,parameters|parametersJsonSchema}]}]`, `toolConfig.functionCallingConfig.mode` (`AUTO|ANY|NONE|VALIDATED`) and `generationConfig{temperature,responseMimeType,responseJsonSchema,thinkingConfig}`.
- **Response**: `candidates[0].content.parts[]` holds `text` or `functionCall{name,args}`. Also returned: `finishReason`, `usageMetadata{promptTokenCount,candidatesTokenCount,thoughtsTokenCount,totalTokenCount}` and `modelVersion`.
- To answer a tool call, append the model turn and then a part containing `{functionResponse:{name,response:{...}}}`.
- To see which IDs your key can use: `GET {base}/models`.
```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL:-gemini-flash-latest}:generateContent" \
  -H "x-goog-api-key: $GEMINI_API_KEY" -H "Content-Type: application/json" -d '{
  "systemInstruction":{"parts":[{"text":"You are an independent risk reviewer for a trading agent."}]},
  "contents":[{"role":"user","parts":[{"text":"Proposed: buy 500 TSLA on 4x margin, 70% of equity. Assess."}]}],
  "tools":[{"functionDeclarations":[{"name":"flag_action","description":"Record a risk verdict",
    "parameters":{"type":"object","properties":{"severity":{"type":"string","enum":["low","medium","high"]},
    "reason":{"type":"string"}},"required":["severity","reason"]}}]}],
  "toolConfig":{"functionCallingConfig":{"mode":"ANY"}}}' | jq '.candidates[0].content.parts[0].functionCall'
# -> {"name":"flag_action","args":{"severity":"high","reason":"Leverage and concentration ..."}}
```
```python
# pip install "google-genai>=2.29,<3"
import os, pathlib
from google import genai
from google.genai import types

client = genai.Client()   # reads GEMINI_API_KEY (GOOGLE_API_KEY wins if both are set)
schema = {"type": "object", "properties": {"transactions": {"type": "array", "items": {"type": "object",
          "properties": {"date": {"type": "string"}, "merchant": {"type": "string"}, "amount": {"type": "number"},
                         "suspicious": {"type": "boolean"}, "reason": {"type": "string"}},
          "required": ["date", "merchant", "amount", "suspicious"]}}}, "required": ["transactions"]}
resp = client.models.generate_content(
    model=os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
    contents=[types.Part.from_bytes(data=pathlib.Path("fixtures/statement.pdf").read_bytes(),
                                    mime_type="application/pdf"),
              "Extract every transaction; mark suspicious ones (duplicates, unusual size, new merchant)."],
    config=types.GenerateContentConfig(temperature=0, response_mime_type="application/json",
                                       response_json_schema=schema))
print(resp.text, resp.usage_metadata.total_token_count)
```
For function calling in Python, pass `types.Tool(function_declarations=[types.FunctionDeclaration(name=..., parameters_json_schema=...)])` and read `resp.function_calls`.

**Model IDs seen in 2026**, from the SDK 2.29.0 model enum and the changelog:
- Aliases: `gemini-flash-latest`, `gemini-flash-lite-latest`, `gemini-pro-latest`.
- Flash: `gemini-3.8-flash` (GA 2 Sep 2026) and `gemini-3.6-flash`.
- Others: `gemini-3.1-flash-lite`, `gemini-3.1-pro-preview`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`.
- Gemma 4: `gemma-4-31b-it`, `gemma-4-26b-a4b-it`.
- TTS: `gemini-3.8-flash-tts`.

Which of these are on the free tier is unverified per model. Check `GET /models` and AI Studio.

## Simulation & free sandbox
There are no test keys. The free tier itself is the sandbox: real outputs, capped per project, and a 429 `RESOURCE_EXHAUSTED` error when you exceed the cap. Google's rate-limit page no longer publishes fixed free numbers; your project's limits appear in AI Studio. Flash and Flash-Lite are free, while Pro, Batch/Flex and Search grounding are reportedly paid-only (search-snippet). The AI Studio playground lets you design a prompt, attach a PDF or image and press "Get code". Typical output is the JSON above: one `functionCall` part, or text, plus `usageMetadata`.

## Visualization ideas
- **Agreement matrix**: Claude's decision vs Gemini's `flag_action.severity` per proposed action. Show a disagreement-rate KPI tile, and route disagreements to a "needs human" lane.
- **Statement → table**: the uploaded PDF on the left, and the extracted `transactions[]` table on the right with `suspicious` rows highlighted and `reason` in a tooltip.
- **Chart-image read-out**: drop in a price-chart screenshot. Gemini returns `{trend, support, resistance}` (your schema), drawn as overlay lines on the image.
- **Cost/latency sparkline**: `usageMetadata.totalTokenCount` and wall-clock time per call, split by model (`modelVersion`).

## Scenarios (official)
Google's docs name these capabilities:
- text generation and chat: `generateContent`, `chats`
- document (PDF) understanding: `inlineData` or the Files API, `POST /upload/v1beta/files`
- image, audio and video understanding: `generateContent`
- function calling: `tools.functionDeclarations`
- structured output: `responseJsonSchema`
- long context and context caching: `cachedContents`
- embeddings: `embedContent`
- grounding with Google Search: the `googleSearch` tool, paid
- Live API for real-time voice: WebSocket `BidiGenerateContent`
- speech generation: the TTS models

## Finance-agent angle
Strong supporting fit, though not as the main brain, since the team's agent runs on Claude. Ways to earn the MLH prize meaningfully (inferred):
1. **Second-opinion risk classifier.** Every action the Claude agent proposes (trade, transfer, client email) also goes to Gemini with a forced `flag_action` tool call. The monitoring dashboard shows where the two vendors agree and where they don't, and a disagreement blocks the action until a human approves. "Two independent models before money moves" is a pitch judges remember.
2. **Multimodal intake.** Gemini reads the uploaded statement PDF, brokerage screenshot or chart image into schema-validated JSON, and the Claude agent works only on that JSON.
3. **Optional:** Gemini TTS reads out high-severity alerts (availability unverified).

In the 2-minute video, show a visible "Gemini" lane in the trace view so the use is obviously load-bearing. Opt into the MLH prize on Devpost (inferred).

## Gotchas
- **Model churn and auto-routing.** Deprecated IDs are silently rerouted to newer models, so behavior can shift mid-hackathon. Log `modelVersion`, replay fixtures for the demo, and keep the ID in `GEMINI_MODEL`.
- **Wrong SDK.** `google-generativeai` / `import google.generativeai` is the legacy package. Use `google-genai`. SDK 3.0 will stop automatic function calling (AFC) from `models.generate_content` (README warning), so pin `<3`.
- **AFC runs your Python functions automatically** when you pass callables as tools. For anything that moves money, pass `FunctionDeclaration`s or set `automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)`, and execute the calls yourself behind your approval gate.
- **Free-tier data use.** Unpaid usage may be used to improve Google products and seen by human reviewers. Use synthetic statements (Faker) only, never real PII.
- **Quotas are per Cloud project, not per key.** Teammates on one project share the RPD. Limits reportedly dropped in Dec 2025 and fluctuate at peak hours (search-snippet).
- **Thinking tokens.** 2.5+/3.x models think by default, which adds latency and `thoughtsTokenCount`. Lower it with `thinkingConfig` (`thinkingLevel: LOW|MINIMAL`; budget semantics per model unverified).
- **Inline-data size.** Inline PDFs/images are limited to about 20 MB per request (unverified). Larger files go through `client.files.upload`.
- **Never ship the key to the browser.** Proxy through your backend.
- The SDK defaults to `v1beta`. "Agent Platform" (`enterprise=True`) is the renamed Vertex AI path, which needs GCP billing. Don't use it for the free tier.

## Mock fallback
Use one adapter: `second_opinion(action) -> {severity, reason}` and `extract_statement(pdf) -> {transactions:[...]}`, switched by `GEMINI_MODE=live|replay`, with `DEMO_MODE=1` forcing replay. In live mode, save each response to `fixtures/gemini/<sha256(model+prompt+file hash)[:16]>.json`. Replay loads the file and fails loudly if it is missing. For unscripted Q&A offline, use a rule stub: leverage > 2x or position > 25% of equity → `high`. A local Gemma 4 through Ollama is a weaker stand-in (fit on a laptop unverified).

## Sources
- https://pypi.org/project/google-genai/ (wheel 2.29.0, 2026-10-07: README, `_api_client.py` base URL/`x-goog-api-key`/`v1beta`, `types.py`, `_gaos/types/interactions/model.py` model enum) (sdk-source)
- https://registry.npmjs.org/@google/genai (2.28.0) (sdk-source)
- https://ai.google.dev/gemini-api/docs/changelog (3.8 Flash GA 2 Sep 2026; 8 Oct 2026 reroutes) (search-snippet)
- https://ai.google.dev/gemini-api/docs/rate-limits and https://www.memetik.ai/guides/gemini-api-free-tier-limits (limits shown in AI Studio, not published) (search-snippet)
- https://pecollective.com/tools/gemini-free-tier-guide/ (Flash/Flash-Lite only on the free tier) (search-snippet)
- https://ai.google.dev/terms (unpaid-service data use, human review) (search-snippet)

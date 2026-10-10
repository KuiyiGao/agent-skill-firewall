---
id: elevenlabs
name: ElevenLabs (Text-to-Speech + ElevenAgents voice agents)
provider: ElevenLabs
category: voice
source: tracks-page
listed_as: "[MLH] Best Use of ElevenLabs"
status: active
cost_model: free-tier
free_allowance: "~10k credits/month (flash/turbo ~0.5 credit/char) + ~10-15 agent minutes/month, no commercial license, attribution required (unverified)"
card_required: false
signup_minutes: 5
auth: "Header xi-api-key: <key>"
base_url: "https://api.elevenlabs.io"
env_vars: [ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, ELEVENLABS_AGENT_ID]
sdks: ["python: elevenlabs==2.71.0", "react: @elevenlabs/react@1.17.0", "browser: @elevenlabs/client@1.27.0", "widget: @elevenlabs/convai-widget-embed@0.19.0"]
sandbox: "No test mode; free tier credits are the sandbox. Cache generated mp3s so re-runs cost nothing."
offline_mock: easy
demo_effect: 5
integration_hours: "1-2 (TTS) / 3-5 (voice agent)"
risk: low
track_fit: [mlh-elevenlabs, hacknc-general]
finance_fit: 4
tags: [voice, tts, speech, voice-agent, alerts, approval, human-in-the-loop, accessibility]
verified: sdk-source
last_checked: 2026-10-10
docs: ["https://elevenlabs.io/docs", "https://github.com/elevenlabs/elevenlabs-python", "https://www.npmjs.com/package/@elevenlabs/react"]
---

## TL;DR
Two useful surfaces. (1) Text-to-Speech: one POST turns text into an mp3; very low risk, 1-2h. (2) ElevenAgents (formerly "Conversational AI"): a voice agent embedded in your page that can call **client tools** (functions running in the browser), so a supervisor can ask "what's pending?" and say "approve it". (2) is the meaningful use that wins the MLH prize; ship (1) first as the fallback.

## Request structure
**TTS:** `POST /v1/text-to-speech/{voice_id}` (stream variant: `/v1/text-to-speech/{voice_id}/stream`; timestamps: `/with-timestamps`).
- Header `xi-api-key`, `Content-Type: application/json`.
- Query: `output_format` (`mp3_44100_128`, `mp3_22050_32`, `pcm_16000`, `ulaw_8000` for phone, `opus_48000_64`), `optimize_streaming_latency` 0-4.
- Body: `text` (required), `model_id`, `voice_settings{stability, similarity_boost, style, speed, use_speaker_boost}`, `language_code`, `seed`, `previous_text`, `next_text`, `apply_text_normalization`.
- Response: raw audio bytes (`audio/mpeg` for mp3).
- Models: `eleven_flash_v2_5` (lowest latency, half price; use for alerts), `eleven_turbo_v2_5`, `eleven_multilingual_v2`, `eleven_v3` (most expressive, audio tags like `[urgent]`). `eleven_v4` / `eleven_v4_turbo` appear in the SDK only for agents/dialogue; confirm with `GET /v1/models` before using them for TTS (unverified).

```bash
curl -X POST "https://api.elevenlabs.io/v1/text-to-speech/$ELEVENLABS_VOICE_ID?output_format=mp3_44100_128" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"text":"Risk alert. Trader agent wants to buy 48 thousand dollars of NVDA. Approval required.","model_id":"eleven_flash_v2_5"}' \
  -o alert.mp3
```
```python
from elevenlabs.client import ElevenLabs          # reads ELEVENLABS_API_KEY
from fastapi.responses import Response
el = ElevenLabs()
def alert_audio(text: str) -> Response:
    chunks = el.text_to_speech.convert(voice_id=VOICE_ID, text=text,
                                       model_id="eleven_flash_v2_5", output_format="mp3_44100_128")
    return Response(b"".join(chunks), media_type="audio/mpeg")   # convert() yields bytes chunks
```
Browser: `new Audio('/api/alerts/' + id + '/audio').play()`.

**Voice agent (ElevenAgents):** create the agent in the dashboard (fastest) or `POST /v1/convai/agents/create`; tools via `POST /v1/convai/tools`, attached by `tool_ids`. Declare each client tool on the agent as type `client` with name, description, parameters and `expects_response: true`.
```tsx
// @elevenlabs/react 1.x: hooks must sit inside <ConversationProvider agentId=...>
useConversationClientTool("get_pending_alerts", async () =>
  (await fetch("/api/alerts?status=pending")).text());
useConversationClientTool("approve_trade", async ({ id }) =>
  (await fetch(`/api/alerts/${id}/approve`, { method: "POST" })).text());
const { startSession, endSession, status, sendContextualUpdate } = useConversation();
// push a new alert into a live session: sendContextualUpdate("New HOLD: ev_0142 NVDA $48k")
```
Plain JS: `Conversation.startSession({ agentId, clientTools: { approve_trade: async ({id}) => ... } })`.
No-code embed: `<elevenlabs-convai agent-id="agent_xxx"></elevenlabs-convai>` + `<script src="https://unpkg.com/@elevenlabs/convai-widget-embed" async></script>`.
Private agents: backend calls `GET /v1/convai/conversation/get-signed-url?agent_id=...` (WebSocket, `startSession({signedUrl})`) or `GET /v1/convai/conversation/token?agent_id=...` (WebRTC, `startSession({conversationToken})`).
Phone: import a Twilio number (`POST /v1/convai/phone-numbers`), then `POST /v1/convai/twilio/outbound-call` with `{agent_id, agent_phone_number_id, to_number, conversation_initiation_client_data:{dynamic_variables:{...}}}`; approvals then need a public **webhook** (server) tool.

## Simulation & free sandbox
There is no test mode; the free tier is the sandbox. A TTS call returns a real mp3 in ~0.3-1s on flash. A voice-agent session is a real two-way conversation in the browser (needs mic permission). To keep credits: generate each alert's audio once and cache the mp3 by alert id; keep agent sessions short during rehearsal.

## Visualization ideas
- Alert toast with a play button and an animated waveform / speaking-orb while audio plays (drive from the `<audio>` element's `timeupdate`).
- "Supervisor console" panel: live transcript of the voice session plus chips for each client-tool call (`approve_trade(ev_0142)` → green).
- Caption track synced with `/with-timestamps` character alignment (karaoke-style highlight of the alert sentence).

## Scenarios (official)
- Narration, audiobooks, voiceovers, accessibility (TTS endpoints).
- Interactive voice agents for customer support and assistants with tools (ElevenAgents; client tools, server/webhook tools, MCP tools with approval via `onMCPToolApprovalRequest`).
- Outbound/inbound phone agents via Twilio or SIP.
- MLH prize copy: "realistic, dynamic, and emotionally expressive voices… from interactive AI companions to narrated stories and voice-enabled apps".

## Finance-agent angle
Strong. Voice is a natural human-in-the-loop channel: a HOLD verdict speaks itself ("Trader agent wants to buy $48k of NVDA for a client with a $25k limit"), and the supervisor approves or rejects by voice through client tools that hit the same approve/reject endpoints as the buttons. Also: spoken end-of-day compliance briefing generated from the audit log (inferred).

## Gotchas
- Browser autoplay is blocked until the user interacts once; add an "Enable alerts" button.
- `@elevenlabs/react` 1.x moved to `ConversationProvider`; `useConversation` outside it fails.
- Client tools must be declared on the agent (dashboard) **and** registered in code, names matching.
- Server/webhook tools need a public URL (ngrok or deploy); client tools do not, prefer them.
- Free tier has no commercial license and requires attribution (unverified); ask the MLH desk for a credit code.
- Mic permission prompts can fail on venue Wi-Fi captive portals or non-HTTPS origins; demo from `localhost` or HTTPS.

## Mock fallback
`VOICE_MODE=cache|live|off`. In `cache`, serve `fixtures/audio/<alert_id>.mp3` recorded during rehearsal; in `off`, use the browser's `speechSynthesis.speak()` so the flow still works. For the voice agent, keep the same approve/reject buttons visible so the demo never depends on the mic.

## Sources
- https://raw.githubusercontent.com/elevenlabs/elevenlabs-python/main/README.md (sdk-source)
- https://pypi.org/pypi/elevenlabs/json, wheel 2.71.0 `text_to_speech/raw_client.py`, `environment.py` (sdk-source)
- https://registry.npmjs.org/@elevenlabs/react, @elevenlabs/client, @elevenlabs/convai-widget-core `.d.ts` (sdk-source)
- https://unite.ai/elevenlabs-launches-eleven-v4-with-low-latency-turbo-variant (search-snippet)
- https://bigvu.tv/blog/elevenlabs-pricing-2026-plans-credits-commercial-rights-api-costs/ (search-snippet)
- https://www.mlh.com/events/prizes (search-snippet)

---
# ---- identity -------------------------------------------------------------
id: twilio
name: Twilio Programmable Messaging + Voice
provider: Twilio Inc.
category: communication
source: resources-doc
listed_as: "Twilio’s Communication APIs"
# ---- availability ---------------------------------------------------------
status: active
cost_model: free-trial
free_allowance: "30-day trial, ~$15 credit, verified recipients only (max 5), sign-up country only; US SMS blocked until toll-free verification (days); test credentials free"
card_required: false
signup_minutes: 15
auth: "HTTP Basic AccountSid:AuthToken (or API Key SID:Secret)"
base_url: "https://api.twilio.com/2010-04-01"
env_vars: [TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, TWILIO_TO_NUMBER, TWILIO_TEST_ACCOUNT_SID, TWILIO_TEST_AUTH_TOKEN, PUBLIC_BASE_URL]
sdks: ["python: twilio==9.11.2", "node: twilio@6.1.2"]
# ---- simulation -----------------------------------------------------------
sandbox: "Test credentials + magic numbers (From +15005550006) return real-shaped JSON, nothing sent or billed; Console Virtual Phone shows trial SMS on screen"
offline_mock: easy
# ---- fit for builders -----------------------------------------------------
demo_effect: 4
integration_hours: "1-2 (outbound SMS/call) / 2-4 (keypad approval webhook)"
risk: medium
track_fit: [hacknc-general, hacknc-community, mlh-elevenlabs, sponsor-finance]
finance_fit: 3
tags: [sms, voice, phone-call, alerts, approval, human-in-the-loop, ivr, 2fa, webhooks]
# ---- provenance -----------------------------------------------------------
verified: search-snippet
last_checked: 2026-10-10
docs: ["https://www.twilio.com/docs", "https://www.twilio.com/docs/iam/test-credentials", "https://www.twilio.com/docs/usage/trials", "https://www.twilio.com/docs/messaging/guides/guide-to-using-the-twilio-virtual-phone", "https://www.twilio.com/docs/voice/twiml/gather"]
---

## TL;DR
The best way for an agent to ask a human: the supervisor's phone rings at the judging table and they press 1 to approve. A new trial in 2026 is tight. You can only reach verified numbers. US SMS is blocked until toll-free verification, which takes days. New-Console trials may also limit SMS bodies to Twilio templates. Plan on four paths: a **voice call with `<Gather>` keypad approval** to a verified phone (works on trial), the **Console Virtual Phone** for on-screen SMS, **test credentials** for CI, and a local mock as the fallback.

## Request structure
Form-encoded POSTs (not JSON), HTTP Basic auth, E.164 numbers (`+19195550123`).
- **SMS:** `POST /Accounts/{AccountSid}/Messages.json`. Fields: `To`, then `From` or `MessagingServiceSid`, then `Body` (or `MediaUrl`), `StatusCallback`.
- **Voice:** `POST /Accounts/{AccountSid}/Calls.json`. Fields: `To`, `From`, `Twiml` (inline XML) or `Url` (a TwiML webhook), `StatusCallback`.
- **Response:** 201 JSON `{sid:"SM…"/"CA…", status:"queued", to, from, body, price:null, error_code:null, date_created, uri}`.
- **Status callbacks:** form POSTs to your URL with `MessageSid`, `MessageStatus` (queued→sent→delivered | undelivered | failed) and `ErrorCode`. For calls: `CallSid`, `CallStatus` (queued, ringing, in-progress, completed, busy, no-answer, failed).
- **`<Gather numDigits="1" action=URL>`** POSTs `Digits`, `CallSid`, `From` and `To` to `action`. That URL must be public HTTPS.

```bash
curl -X POST "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Calls.json" \
  -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN" \
  --data-urlencode "To=$TWILIO_TO_NUMBER" --data-urlencode "From=$TWILIO_FROM_NUMBER" \
  --data-urlencode "Twiml=<Response><Gather numDigits=\"1\" action=\"$PUBLIC_BASE_URL/twilio/decision?req=42\"><Say>Trader agent requests a large buy. Press 1 to approve, 2 to reject.</Say></Gather><Say>No input. Rejected.</Say></Response>"
# SMS: same shape against /Messages.json with --data-urlencode 'Body=Risk alert: agent T-7 hit its limit'
```
```python
import os
from fastapi import FastAPI, Form, Response
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather

tw = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
BASE = os.environ["PUBLIC_BASE_URL"]            # e.g. a cloudflared/ngrok https URL

def request_approval(req_id: str, summary: str) -> str:
    vr = VoiceResponse()
    g = Gather(num_digits=1, action=f"{BASE}/twilio/decision?req={req_id}", method="POST")
    g.say(f"{summary}. Press 1 to approve, 2 to reject.")
    vr.append(g); vr.say("No input received. Rejected.")
    call = tw.calls.create(to=os.environ["TWILIO_TO_NUMBER"], from_=os.environ["TWILIO_FROM_NUMBER"],
                           twiml=str(vr), status_callback=f"{BASE}/twilio/status")
    return call.sid                                   # "CA…", status "queued"

app = FastAPI()                                       # Form() needs python-multipart
@app.post("/twilio/decision")
async def decision(req: str, Digits: str = Form("")):
    approved = Digits == "1"                          # push to dashboard / audit log here
    return Response(f"<Response><Say>{'Approved' if approved else 'Rejected'}.</Say></Response>",
                    media_type="text/xml")
# SMS: tw.messages.create(to=..., from_=..., body="...", status_callback=f"{BASE}/twilio/status")
```

## Simulation & free sandbox
- **Test credentials.** These are a separate Test Account SID and Test Auth Token, found in Console → API keys & tokens → Test credentials. They work only with Messages, Calls, IncomingPhoneNumbers and Lookup. Any other resource returns 403 (error 20008). Nothing is sent, charged or logged.
  - Magic `From` numbers: `+15005550006` succeeds, `+15005550001` is invalid (21212), `+15005550007` is not owned (21606), `+15005550008` is a full queue (21611).
  - Magic `To` numbers: `+15005550001` is invalid (21211), `+15005550002` can't be routed (21612), `+15005550003` has no international permission (21408), `+15005550004` is blocked (21610), `+15005550009` is not SMS-capable (21614). Any other number succeeds. These error codes are from memory (unverified).
  - What you get back: the normal 201 JSON with `status:"queued"`. No status callbacks follow (unverified).
  - The docs say **new test credentials can't be created in the new Console**. Ones made in the legacy Console still work. If your account has none, use the mock.
- **Virtual Phone** (Console → Messaging → Virtual Phone; documented for legacy-Console trials). It is a simulated handset in the browser with a Twilio-owned number. SMS your app sends to it shows up as chat bubbles, which you can screen-record for the demo video.
- **Trial credit (~$15).** Real calls and SMS go to up to 5 verified numbers. Calls play a trial preamble before your TwiML runs. Some TwiML verbs are blocked on trial (which ones is unverified). SMS bodies start with "Sent from a Twilio Trial account".
- **Lookup magic numbers** exist for testing SIM-swap and line-type checks (`/docs/lookup/magic-numbers-for-lookup`).

## Visualization ideas
- **Approval timeline:** agent request → call ringing → `Digits` → approved/rejected. Status chips come from `CallStatus`/`MessageStatus` callbacks.
- **Phone mockup panel** in the dashboard that mirrors each outbound `Body` with delivery ticks (queued/sent/delivered).
- **Escalation Sankey:** alerts by severity → channel (SMS/voice) → outcome (approved/rejected/timeout).
- **Human-latency histogram:** seconds from agent flag to `Digits` received, per supervisor.

## Scenarios (official)
- Alerts and notifications by SMS/MMS (`Messages.json`).
- IVR and phone trees that collect keypad or speech input (`Calls.json` + TwiML `<Gather>`).
- Two-factor / one-time codes with the Verify API (`verify.twilio.com/v2/Services/{sid}/Verifications`). Trial Verify uses a test template.
- Fraud checks with Lookup v2 line type / SIM swap (`lookups.twilio.com/v2/PhoneNumbers/{number}?Fields=…`).
- AI voice agents over a call with ConversationRelay (details unverified).

## Finance-agent angle
Good fit as the **human-in-the-loop channel**, not as a data source.
- An agent action above a threshold places a call; the supervisor presses 1 or 2 and the decision is written to the audit log.
- Step-up auth with Verify before an agent moves money.
- A Lookup SIM-swap check before a payout, as a fraud-prevention story.
- For the ElevenLabs prize, `<Play>` an ElevenLabs mp3 hosted at a public URL instead of `<Say>`.

## Gotchas
- **US SMS on a trial won't work today:**
  - 10DLC registration needs a paid account plus campaign vetting.
  - Trial toll-free numbers are blocked with error 30032 until toll-free verification, which takes days.
  - Use voice or the Virtual Phone instead.
- **Trial limits:** verified recipients only (up to 5), sign-up country only, trial prefix and preamble. New-Console trials say SMS is "template only, no custom bodies". Whether the REST API enforces that is unverified, so test in your first 15 minutes.
- **Webhooks need a public HTTPS URL.** `cloudflared tunnel --url http://localhost:8000` needs no account; ngrok needs one. If you validate `X-Twilio-Signature` (`twilio.request_validator.RequestValidator`), the URL must match the tunnel URL exactly.
- **Python parameter is `from_`**, not `from`. Requests are form-encoded. Numbers must be E.164.
- **`<Gather>` waits about 5 s by default**, then falls through to the next verb (unverified). Say the prompt first and keep it short.
- **Demo-floor risk:** a phone on silent, a noisy hall, weak cell signal. Mirror every event on screen.
- **Secrets:** never commit the Auth Token. Prefer an API Key (SK…) and secret.

## Mock fallback
- **Interface:** one `Notifier` with `send_sms(to, body)` and `request_approval(req_id, summary) -> sid`. Pick the implementation with `TWILIO_MODE=mock|test|live` (`DEMO_MODE=1` forces `mock`). `test` uses the test credentials plus `+15005550006`.
- **Mock implementation:** returns fake SIDs (`"SM" + uuid4().hex[:8]`) and pushes events over SSE/WebSocket to the dashboard's phone panel. An asyncio timer plays queued→sent→delivered over about 2 s.
- **Approval in the mock:** an on-screen "keypad" (buttons 1/2) or a hotkey posts the same `/twilio/decision` payload (`Digits=1`). The rest of the app can't tell mock from live.

## Sources
- https://www.twilio.com/docs/iam/test-credentials (search-snippet: supported resources, 403, new-Console note)
- https://www.twilio.com/en-us/blog/using-test-credentials-magic-phone-numbers-twilio-applications (search-snippet: magic numbers)
- https://www.twilio.com/docs/messaging/tutorials/automate-testing (search-snippet: +15005550006 as From)
- https://www.twilio.com/docs/usage/trials and https://www.twilio.com/docs/usage/tutorials/how-to-use-your-free-trial-account (search-snippet: template-only SMS, 5 recipients, sign-up country)
- https://www.twilio.com/docs/usage/trials/try-out-voice (search-snippet: custom TwiML allowed, some verbs blocked)
- https://www.twilio.com/docs/messaging/guides/guide-to-using-the-twilio-virtual-phone (search-snippet)
- https://support.twilio.com/hc/en-us/articles/11853148778523 and https://www.twilio.com/docs/api/errors/30032 (search-snippet: toll-free / 10DLC)
- https://pypi.org/pypi/twilio/json and https://registry.npmjs.org/twilio/latest (sdk-source: 9.11.2 / 6.1.2)
- Magic-number error codes, Gather timeout default (memory)

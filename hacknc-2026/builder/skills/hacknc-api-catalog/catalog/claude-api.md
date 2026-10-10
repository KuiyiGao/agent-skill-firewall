---
id: claude-api
name: Claude API (Messages + tool use, Anthropic Python SDK)
provider: Anthropic
category: llm
source: extra
listed_as: ""
status: active
cost_model: paid-only
free_allowance: "Pay-as-you-go; Opus 5.5 $4/$20, Sonnet 5.5 $2/$10, Haiku 5.5 $0.10/$0.50 per 1M input/output tokens; any free credits depend on your account"
card_required: true
signup_minutes: 10
auth: "Header x-api-key: <key> (SDK reads ANTHROPIC_API_KEY)"
base_url: "https://api.anthropic.com/v1/messages"
env_vars: [ANTHROPIC_API_KEY]
sdks: ["python: anthropic==1.13.0", "node: @anthropic-ai/sdk (version unverified)"]
sandbox: "No sandbox; cache responses for scripted demo scenes (replay mode)"
offline_mock: medium
demo_effect: 3
integration_hours: "2-3 (3 agents with tools)"
risk: low
track_fit: [hacknc-general]
finance_fit: 5
tags: [llm, agents, tool-use, function-calling, human-in-the-loop, approval-gate]
verified: sdk-source
last_checked: 2026-10-10
docs: ["https://platform.claude.com/docs", "https://github.com/anthropics/anthropic-sdk-python"]
---

## TL;DR
The agent brain. The SDK's **tool runner** drives the tool-use loop for you, and a human-approval gate fits *inside* each tool function: `await` an approval future and return a "held/declined" result if the supervisor says no. Default model `claude-opus-5-5`; lower `effort` for snappy demo turns.

## Request structure
Everything is `POST /v1/messages` (headers `x-api-key`, `anthropic-version`, `content-type`). Tools are declared in `tools`; the model replies with `tool_use` blocks; you send back `tool_result` blocks with the matching `tool_use_id`.

```python
# pip install anthropic==1.13.0   (verified offline: async runner + gated tool)
import asyncio, json
from anthropic import AsyncAnthropic, beta_async_tool
client = AsyncAnthropic()                                   # reads ANTHROPIC_API_KEY

@beta_async_tool
async def place_order(client_id: str, symbol: str, side: str, notional: float) -> str:
    """Place a market order for a client account.

    Args:
        client_id: Client ID, e.g. C-1042.
        symbol: Ticker.
        side: "buy" or "sell".
        notional: Dollar amount.
    """
    verdict = await gate("trader", "place_order", {"client_id": client_id, "symbol": symbol,
                                                   "side": side, "notional": notional})
    if verdict != "PASS":
        return json.dumps({"status": "stopped_by_supervision", "verdict": verdict})
    return json.dumps(broker_submit(symbol, side, notional))

runner = client.beta.messages.tool_runner(
    model="claude-opus-5-5", max_tokens=16000, system=TRADER_PROMPT,
    tools=[place_order], output_config={"effort": "low"}, max_iterations=8,
    betas=["server-side-fallback-2026-07-01"], fallbacks="default",   # auto-retry on refusal
    messages=[{"role": "user", "content": task}])
async for message in runner:            # each assistant turn, before tools run
    publish_trace(message)
```
`@beta_async_tool` builds the JSON schema from the signature and docstring (`additionalProperties: false`, all args required).

## Simulation & free sandbox
No free sandbox. For a reliable demo, record each scripted scenario once and replay the recorded model turns (key them by a hash of the request messages) so the demo works on bad Wi-Fi and behaves identically every time.

## Visualization ideas
- Agent trace column: each assistant turn as a card (thinking-free text, tool calls as chips with args).
- Tool-call graph: agent → tool → external host edges, colored by gateway verdict.
- Token/cost meter per agent from `response.usage`.

## Scenarios (official)
- Custom agents with your own tools via the tool runner or a manual loop; human-in-the-loop approval gates inside tool functions; structured outputs; prompt caching (Claude API docs).

## Finance-agent angle
Core: research, trading and client-service agents are tool-using Claude loops; the supervision gateway wraps every tool function.

## Gotchas
- `claude-opus-5-5` rejects forced `tool_choice` (`any` / `tool`) with a 400; use `auto` and say which tool to use in the prompt.
- Thinking cannot be disabled on Opus 5.5; control depth and latency with `output_config.effort` (default `medium`).
- Modern Claude models resist prompt injection well: do not build a demo that depends on the model obeying an injected instruction; make the dangerous action come from skill code, and show the gateway quarantining the injected text.
- Always return a `tool_result` for every `tool_use` (use `is_error: true` on failure).

## Mock fallback
`LLM_MODE=live|replay`: in replay, return the recorded `tool_use` / text turns from `fixtures/llm/<scenario>.json`; the gateway and dashboard run unchanged.

## Sources
- anthropic 1.13.0 wheel from https://pypi.org/pypi/anthropic/json: `resources/beta/messages/messages.py` (`tool_runner` signature incl. `fallbacks`, `betas`, `max_iterations`), `lib/tools/_beta_runner.py` (`__aiter__`, `until_done`) (sdk-source)
- Claude API skill reference bundled with Claude Code (official-docs)

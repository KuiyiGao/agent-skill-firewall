---
# ---- identity -------------------------------------------------------------
id: example-api                 # kebab-case, MUST equal the file name (example-api.md)
name: Example API               # human name
provider: Example Inc.
category: communication         # see "Enums" in ../SKILL.md
source: resources-doc           # resources-doc | tracks-page | extra
listed_as: "Example's APIs"     # exact label as written on the HackNC page ("" for extra)
# ---- availability ---------------------------------------------------------
status: active                  # active | changed | legacy | dead | unknown
cost_model: free-tier           # free | free-tier | free-trial | campus-license | paid-only | unknown
free_allowance: "1,000 req/month, no card"   # one line, concrete numbers, say 'unverified' if unsure
card_required: false            # true | false | unknown
signup_minutes: 5               # realistic time from zero to a working key
auth: "Header X-Api-Key: <key>"
base_url: "https://api.example.com/v1"
env_vars: [EXAMPLE_API_KEY]     # the env var names our code reads
sdks: ["python: example==1.2.3", "node: example@4.5.6"]   # pinned, latest checked
# ---- simulation -----------------------------------------------------------
sandbox: "Test keys return canned data; no real side effects"   # free simulation mode, or "none"
offline_mock: easy              # easy | medium | hard  (how hard to fake it locally)
# ---- fit for builders -----------------------------------------------------
demo_effect: 3                  # 1-5  how good it looks in a 2-minute demo
integration_hours: "1-2"        # realistic, for one person, including signup
risk: low                       # low | medium | high  (signup friction, quotas, flaky)
track_fit: [hacknc-general]     # prize ids from ../references/tracks.md
finance_fit: 2                  # 1-5  usefulness for finance-agent monitoring / fin-co agents
tags: [sms, alerts]
# ---- provenance -----------------------------------------------------------
verified: sdk-source            # weakest evidence behind the key claims:
                                # sdk-source | official-docs | search-snippet | memory
last_checked: 2026-10-10
docs: ["https://docs.example.com"]
---

## TL;DR
Two or three sentences: what it is, what is free, the one thing a builder should know first.

## Request structure
Exact endpoint(s), method, headers, body/query fields, and response shape.
Give ONE minimal raw HTTP example (curl) and ONE SDK example (Python unless the
API is browser-only). Keep examples copy-pasteable with env vars, never real keys.

## Simulation & free sandbox
What you can do for free without real side effects (test credentials, devnet,
paper trading, trial credits, magic values). What the simulated result looks like.

## Visualization ideas
2-4 concrete UI/visual forms this data or action supports (e.g. "map heat layer
of X", "timeline of Y with status chips"), with the field(s) that drive each.

## Scenarios (official)
Use cases the provider's own docs/marketing name, paraphrased, each with the
endpoint that serves it. Mark anything you inferred yourself as (inferred).

## Finance-agent angle
How this fits an AI-agent monitoring / financial-firm agent project, or "weak fit" and why.

## Gotchas
Bulleted traps: quotas, deprecations, CORS, auth quirks, versions, weekend behavior.

## Mock fallback
How to fake it locally behind the same interface (fixture file, stub server,
seeded generator) so a demo survives bad Wi-Fi.

## Sources
Bullet list of URLs actually used, each tagged with the evidence level
(sdk-source / official-docs / search-snippet / memory).

---
id: capital-one-nessie
name: Capital One Nessie (hackathon mock banking API)
provider: Capital One
category: finance-data
source: extra
listed_as: ""
status: dead
cost_model: free
free_allowance: "Was free with a key from the Nessie site; reported down since 2025 (unverified)"
card_required: false
signup_minutes: 10
auth: "Query param ?key=<key>"
base_url: "http://api.nessieisreal.com"
env_vars: [NESSIE_API_KEY]
sdks: ["none current (nessieisreal/nessie-android-sdk, last commit 2017)"]
sandbox: "The whole API was a sandbox of fake customers, accounts and transactions"
offline_mock: easy
demo_effect: 2
integration_hours: "1 (if alive)"
risk: high
track_fit: [sponsor-finance]
finance_fit: 3
tags: [banking, accounts, transactions, mock, capital-one]
verified: search-snippet
last_checked: 2026-10-10
docs: ["https://github.com/nessieisreal/nessie-android-sdk"]
---

## TL;DR
Listed here so nobody wastes time: Capital One's hackathon banking sandbox, which a HackMTY 2026 team reports "went down mid-competition in 2025 and didn't come back" (unverified; the host is blocked from this sandbox). It is retail banking, not brokerage. If a Capital One prize appears at HackNC, ask their reps whether Nessie is live; otherwise reproduce its shapes locally.

## Request structure
From the official Android SDK (2017): base `http://api.nessieisreal.com` (older alias `api.reimaginebanking.com`), key as `?key=`.
- `GET /customers`, `GET /customers/{id}/accounts`
- `GET|POST /accounts/{id}/purchases|deposits|withdrawals|transfers|bills`
- `GET /atms?lat=&lng=&rad=`, `/enterprise/*`
```bash
curl "http://api.nessieisreal.com/customers?key=$NESSIE_API_KEY"
```

## Simulation & free sandbox
It was entirely simulated (fake customers, accounts, purchases). Current availability unknown.

## Visualization ideas
- Account balance cards and a transaction ledger.
- ATM map (pairs with a maps entry).

## Scenarios (official)
- Hackathon apps on mock banking data: budgeting, payments, transfers (Capital One hackathon resource; inferred from SDK endpoints).

## Finance-agent angle
Would give a client-service agent account/transfer tools; replicate locally instead.

## Gotchas
- Plain HTTP, old SDKs, possibly offline. Do not make a demo depend on it.

## Mock fallback
Serve the same paths from a local stub backed by `faker` data (`/customers`, `/accounts/{id}/transfers`).

## Sources
- https://github.com/nessieisreal/nessie-android-sdk (sdk-source, 2017)
- https://github.com/DiegoGalloM/HackMTY2026 README lines 373-377 (search-snippet)
- WEHack 2026 Devpost mention of Nessie as an optional Capital One API (search-snippet)

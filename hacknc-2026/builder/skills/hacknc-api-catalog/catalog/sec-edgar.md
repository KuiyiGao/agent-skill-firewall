---
id: sec-edgar
name: SEC EDGAR APIs (submissions, XBRL facts, full-text search)
provider: U.S. Securities and Exchange Commission
category: finance-data
source: extra
listed_as: ""
status: active
cost_model: free
free_allowance: "Free, no key; max 10 requests/second; descriptive User-Agent required"
card_required: false
signup_minutes: 0
auth: "None; header User-Agent: <Org Name> <contact email>"
base_url: "https://data.sec.gov"
env_vars: [SEC_USER_AGENT]
sdks: ["python: requests (no official SDK); edgartools is a popular community wrapper (version unverified)"]
sandbox: "Public read-only data; nothing to simulate"
offline_mock: easy
demo_effect: 2
integration_hours: "1"
risk: low
track_fit: [hacknc-general, sponsor-finance]
finance_fit: 4
tags: [filings, 10-k, 10-q, 8-k, fundamentals, xbrl, research-agent]
verified: search-snippet
last_checked: 2026-10-10
docs: ["https://www.sec.gov/edgar/sec-api-documentation", "https://www.sec.gov/os/accessing-edgar-data"]
---

## TL;DR
Free official filings and XBRL financial facts for every US public company, no key. Good for a research agent that cites real 10-K numbers. Call it from the backend (no CORS) with a descriptive User-Agent, or you get 403s.

## Request structure
- `GET https://data.sec.gov/submissions/CIK##########.json` (10-digit zero-padded CIK): company profile + `filings.recent` arrays (form, filingDate, accessionNumber, primaryDocument).
- `GET https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`: all XBRL facts by taxonomy/concept/unit.
- `GET https://data.sec.gov/api/xbrl/companyconcept/CIK##########/us-gaap/Revenues.json`: one concept over time.
- `GET https://www.sec.gov/files/company_tickers.json`: ticker → CIK map.
- Full-text search (undocumented, unverified): `https://efts.sec.gov/LATEST/search-index?q="..."&forms=10-K&startdt=YYYY-MM-DD&enddt=YYYY-MM-DD`.

```bash
curl -H "User-Agent: $SEC_USER_AGENT" https://data.sec.gov/submissions/CIK0000320193.json
```
```python
import os, requests
H = {"User-Agent": os.environ["SEC_USER_AGENT"]}   # e.g. "HackNC Team team@example.edu"
subs = requests.get("https://data.sec.gov/submissions/CIK0000320193.json", headers=H, timeout=10).json()
print(subs["name"], subs["filings"]["recent"]["form"][:5])
```

## Simulation & free sandbox
Public data, read-only. Cache the handful of companies you demo into `fixtures/edgar/` so the research agent works offline.

## Visualization ideas
- Revenue / net income sparkline per ticker from `companyconcept`.
- Filing timeline (8-K dots, 10-Q/10-K bars) beside the news feed.
- "Source" citation chips on agent answers linking to the filing.

## Scenarios (official)
- Programmatic access to company submissions history and XBRL financial statement data (EDGAR API docs).
- Bulk downloads (nightly ZIPs) for large-scale analysis.

## Finance-agent angle
Good grounding source: an agent claim like "NVDA revenue grew X%" can be checked against `companyconcept`, and the dashboard can flag unsupported numbers (inferred).

## Gotchas
- Missing or generic User-Agent → 403. Keep under 10 req/s or you get temporarily blocked.
- data.sec.gov does not allow browser CORS requests (from memory); proxy through your backend.
- CIKs must be zero-padded to 10 digits.

## Mock fallback
Save the JSON responses for 3-5 tickers in `fixtures/edgar/<cik>.json`; serve them from a local route with the same paths.

## Sources
- https://www.sec.gov/edgar/sec-api-documentation (search-snippet)
- https://www.sec.gov/os/accessing-edgar-data (search-snippet)
- https://orthogonal.info/sec-edgar-full-text-search-api-efts-python/ (search-snippet)

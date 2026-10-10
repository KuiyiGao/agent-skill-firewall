---
id: faker
name: Faker (synthetic PII / clients / transactions)
provider: joke2k/faker (open source)
category: synthetic-data
source: extra
listed_as: ""
status: active
cost_model: free
free_allowance: "Open source (MIT), fully offline"
card_required: false
signup_minutes: 0
auth: "None (local library)"
base_url: "n/a (pip install faker)"
env_vars: [FAKER_SEED]
sdks: ["python: Faker==40.43.0", "node: @faker-js/faker (version unverified)"]
sandbox: "Everything is simulated: deterministic fake people, SSNs, addresses, bank accounts with a fixed seed"
offline_mock: easy
demo_effect: 1
integration_hours: "0.5"
risk: low
track_fit: [hacknc-general]
finance_fit: 4
tags: [synthetic-data, pii, mock, clients, seed-data, offline]
verified: sdk-source
last_checked: 2026-10-10
docs: ["https://faker.readthedocs.io", "https://github.com/joke2k/faker"]
---

## TL;DR
The safe way to have "client PII" in a demo: realistic-looking but fake names, SSNs, emails, addresses and account numbers, identical on every run with a fixed seed. Pair it with SQLite and you have a fictional brokerage's client book in 30 minutes.

## Request structure
Local library calls, no network.
```python
# pip install Faker==40.43.0
import random
from faker import Faker
fake = Faker("en_US"); Faker.seed(2026); random.seed(2026)

def make_client(i: int) -> dict:
    return {
        "client_id": f"C-{1000 + i}",
        "name": fake.name(), "email": fake.email(), "ssn": fake.ssn(),
        "dob": fake.date_of_birth(minimum_age=21, maximum_age=85).isoformat(),
        "address": fake.address().replace("\n", ", "),
        "account_no": fake.bban(),
        "risk_profile": random.choice(["conservative", "balanced", "aggressive"]),
        "cash_usd": round(random.uniform(5_000, 250_000), 2),
        "trade_limit_usd": random.choice([10_000, 25_000, 50_000]),
    }

clients = [make_client(i) for i in range(50)]
```
Useful providers: `name`, `ssn`, `bban`/`iban`, `credit_card_number`, `company`, `date_time_between`, `pyfloat`, `ipv4`, `user_agent`.

## Simulation & free sandbox
Fully simulated and offline. With `Faker.seed(N)` the same 50 clients come back every run, so screenshots, the replay cache and the video stay consistent.

## Visualization ideas
- Client table with PII columns masked by default (`***-**-1234`); unmask on click to show what an agent would have leaked.
- PII "taint" highlight: when a blocked outbound payload contains a client's SSN or account number, highlight the matching cells.
- Synthetic transaction stream for a fraud/anomaly chart (amount over time with flagged points).

## Scenarios (official)
- Generating fake data for testing, bootstrapping databases, anonymizing data and stress tests (Faker docs).

## Finance-agent angle
Essential plumbing: lets you demo PII exfiltration blocking without touching real personal data, and gives the PII-taint rule known values to match on.

## Gotchas
- Fake SSNs can still look real; label the dataset "synthetic" in the UI and README.
- Locale matters (`en_US` for SSN format).
- Seed both `Faker` and `random` if you mix them.

## Mock fallback
It is the mock. Write the generated rows to `fixtures/clients.json` and commit it so nobody has to regenerate.

## Sources
- https://pypi.org/pypi/Faker/json (sdk-source; snippet run locally with 40.43.0)
- https://github.com/joke2k/faker (sdk-source)

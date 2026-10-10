---
id: alpaca-paper-trading
name: Alpaca Trading API (paper account)
provider: Alpaca Markets
category: finance-trading
source: extra
listed_as: ""
status: active
cost_model: free
free_allowance: "Paper-only account with email signup, no KYC, $100k simulated cash by default; free IEX market-data feed"
card_required: false
signup_minutes: 10
auth: "Headers APCA-API-KEY-ID + APCA-API-SECRET-KEY (paper keys differ from live keys)"
base_url: "https://paper-api.alpaca.markets"
env_vars: [ALPACA_API_KEY, ALPACA_SECRET_KEY, BROKER]
sdks: ["python: alpaca-py==0.44.0 (Python 3.10+)"]
sandbox: "Paper trading is the simulation: real order lifecycle (accepted/new/filled/rejected), real buying-power checks, simulated fills at market prices"
offline_mock: easy
demo_effect: 3
integration_hours: "1-2"
risk: low
track_fit: [hacknc-general, sponsor-finance]
finance_fit: 5
tags: [trading, orders, brokerage, paper-trading, portfolio, positions, simulation]
verified: sdk-source
last_checked: 2026-10-10
docs: ["https://docs.alpaca.markets/docs/paper-trading", "https://docs.alpaca.markets/docs/orders-at-alpaca", "https://github.com/alpacahq/alpaca-py"]
---

## TL;DR
The easiest real brokerage sandbox: sign up with an email, get paper keys, place orders that go through a real order lifecycle with simulated fills. On a weekend, stock `day` orders are accepted and queued for Monday's open, which is fine for a demo ("queued until Mon 9:30 ET"). The same SDK can point at a local mock server via `url_override`.

## Request structure
- `POST /v2/orders` body: `symbol`, `side` (buy|sell), `type` (market|limit|stop|stop_limit|trailing_stop), `time_in_force` (day|gtc|opg|cls|ioc|fok), exactly one of `qty` or `notional`, optional `limit_price`, `extended_hours`, `client_order_id`. Sending both qty and notional → 400.
- `GET /v2/account` (cash, buying_power, equity, status), `GET /v2/positions`, `GET /v2/orders?status=open`, `GET /v2/clock` (`is_open`, `next_open`), `DELETE /v2/orders` (cancel all).

```bash
curl -X POST https://paper-api.alpaca.markets/v2/orders \
  -H "APCA-API-KEY-ID: $ALPACA_API_KEY" -H "APCA-API-SECRET-KEY: $ALPACA_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","qty":"10","side":"buy","type":"market","time_in_force":"day"}'
```
```python
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
tc = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)
# tc = TradingClient(KEY, SECRET, paper=True, url_override="http://127.0.0.1:8001")  # local mock
print(tc.get_clock().is_open, tc.get_account().buying_power)
o = tc.submit_order(MarketOrderRequest(symbol="AAPL", qty=10, side=OrderSide.BUY,
                                       time_in_force=TimeInForce.DAY))
print(o.status)   # weekend → OrderStatus.ACCEPTED (sometimes NEW)
```

## Simulation & free sandbox
- Paper account starts with $100k; reset gives new keys.
- Weekend/closed market: `day` orders submitted after the close are queued for the next trading day, status usually `accepted`. OPG rejected 9:28am-7pm ET, CLS 3:50-7pm ET.
- Real rejections still happen: buying power is checked at submit (market buys valued ~2.5-4% above last price) → `403 {"code":40310000,"message":"insufficient buying power"}`.
- Crypto (`BTC/USD`, `gtc`/`ioc`) trades 24/7 and paper simulates it, so you can show a real fill on a weekend (unverified for every account; try once).

## Visualization ideas
- Order lifecycle chips (HELD → APPROVED → ACCEPTED/QUEUED → FILLED) on the agent-event timeline.
- Portfolio panel: positions table + allocation donut from `/v2/positions`.
- "Market closed, queued until <next_open>" badge from `/v2/clock`.
- Buying-power gauge that turns red when an agent's order would exceed it.

## Scenarios (official)
- Paper trading to test strategies and apps before going live (paper-trading docs).
- Algorithmic trading via REST/WebSocket; fractional and notional orders; crypto trading.
- Broker API for building brokerage apps (separate product, not needed here).

## Finance-agent angle
Core. A trading agent's `place_order` tool calls this behind the supervision gateway; HOLD verdicts block the call until a human approves, then the order really reaches the paper broker. Rejections (buying power) become another visible failure mode.

## Gotchas
- Fractional/notional orders only as market + `day`; not in extended hours.
- `extended_hours: true` needs a limit order with `day` (newer docs also allow `gtc`).
- Weekend demo: status shows `accepted`/`new`; render both as "QUEUED".
- Run `DELETE /v2/orders` after the demo so queued orders don't fill Monday.
- Free data feed is IEX only (thin prices); cache Friday closes for limit checks.

## Mock fallback
Write a ~60-line stub that serves `/v2/clock`, `/v2/account`, `/v2/positions`, `/v2/orders` with Alpaca's JSON shapes and point `TradingClient(url_override=...)` at it; tested to parse correctly with alpaca-py 0.44.0 (order returns `OrderStatus.ACCEPTED`). Switch with `BROKER=alpaca|mock`.

## Sources
- https://raw.githubusercontent.com/alpacahq/alpaca-py/master/ `alpaca/common/rest.py`, `trading/requests.py`, `trading/enums.py`, `README.md` (sdk-source)
- https://pypi.org/pypi/alpaca-py/json (sdk-source)
- https://github.com/alpacahq/alpaca-docs `content/trading/orders.md`, `paper-trading.md` (official-docs, archived)
- https://docs.alpaca.markets/docs/orders-at-alpaca, https://docs.alpaca.markets/docs/paper-trading (search-snippet)
- https://forum.alpaca.markets/t/alpaca-api-throwing-incorrect-error-message-when-order-placed-is-far-below-available-dt-buying-power/13861 (search-snippet)

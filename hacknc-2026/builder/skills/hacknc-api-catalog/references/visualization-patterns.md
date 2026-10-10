# Visualization patterns across the catalog

Each catalog entry lists its own visualization ideas. This file collects the patterns that
recur, so a builder can pick a coherent set instead of one widget per API.

## Pick by data shape

| Data shape | Good form | Typical sources |
|---|---|---|
| Stream of discrete events with a status | Vertical timeline with status chips; filter by actor | agent tool calls, orders, SMS/call status callbacks, anchors |
| Actor → action → target relationships | Node-link graph (React Flow / Cytoscape), edges colored by verdict | agent → tool → host, money flows |
| Value over time | Line/area chart; sparklines in table rows | prices, revenue facts (EDGAR), time-series DB aggregates |
| Category × time counts | Heatmap | news per ticker per day, alerts per agent per hour |
| Places | Map with markers, clusters, heat layer, route lines | maps entries, ATM/branch data |
| Part of whole | Donut / stacked bar (sparingly) | portfolio allocation, verdict mix |
| One headline number | KPI tile with delta | blocked attempts, approval latency, cost per anchor |
| Audio / speech | Waveform or speaking-orb + live captions | ElevenLabs |
| Proof / integrity | Checklist with green checks and the first red break | Solana anchors, hash chains |

## Verdict / status color semantics (keep consistent everywhere)

- PASS / success: aqua-green
- HOLD / pending human: amber
- BLOCK / failure: coral red
- QUEUED / neutral system state: slate blue

Use color plus an icon or label, never color alone.

## Frutiger Aero styling (for the `hacknc-frutiger-aero` track)

The look: early-2010s optimism, glossy glass, water, sky, bubbles, green-blue palette.

```css
:root {
  --sky-top: #bfe9ff; --sea-bottom: #2ba7c9; --leaf: #7ed957;
  --glass: rgba(255,255,255,.28); --glass-edge: rgba(255,255,255,.65);
}
body { background: linear-gradient(180deg, var(--sky-top), var(--sea-bottom)); }
.panel {
  background: var(--glass);
  backdrop-filter: blur(14px) saturate(140%);
  border: 1px solid var(--glass-edge);
  border-radius: 18px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,.8), 0 8px 24px rgba(0,60,90,.18);
}
.panel::before {                 /* top gloss highlight */
  content: ""; position: absolute; inset: 0 0 55% 0; border-radius: 18px 18px 40% 40%;
  background: linear-gradient(rgba(255,255,255,.55), rgba(255,255,255,0));
  pointer-events: none;
}
.pill-button {
  border-radius: 999px; border: 1px solid #1d8fb3;
  background: linear-gradient(#e9fbff, #8fdcf2 49%, #49c0e3 51%, #9ae6f7);
}
```
Ideas: graph nodes drawn as glass bubbles, slow floating bubble particles in the
background, a water-level meter for risk, rounded "Vista" fonts (Segoe UI, or Nunito from
Google Fonts as a fallback). Keep text contrast high on glass (dark text, or a solid
backing behind dense tables).

## Dashboard layout that demos well in 2 minutes

1. Top row: 3-4 KPI tiles (today's actions, held, blocked, verified).
2. Center: the relationship graph (the "wow" visual) with live edge animation.
3. Right: event timeline with verdict chips; clicking an event opens its detail.
4. Bottom or modal: the human action (approve/reject, verify, play alert).

One scenario button per demo scene ("Run: poisoned news", "Run: over-limit trade",
"Run: tamper test") makes the demo repeatable at the table.

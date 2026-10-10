---
id: solana
name: Solana (devnet + SPL Memo program)
provider: Solana Foundation / Anza
category: blockchain
source: tracks-page
listed_as: "[MLH] Best Use of Solana"
status: active
cost_model: free
free_allowance: "devnet SOL is free from faucets; 1 SOL pays ~200k memo txs at 5000 lamports/signature (fee unverified)"
card_required: false
signup_minutes: 10
auth: "None for RPC; transactions signed with a local ed25519 keypair (64-int JSON array file)"
base_url: "https://api.devnet.solana.com"
env_vars: [SOLANA_RPC, SOLANA_KEYPAIR_PATH]
sdks: ["python: solana==0.41.0 + solders==0.29.0", "node: @solana/web3.js@1.99.0", "node: @solana/kit@8.4.0 + @solana-program/memo@0.15.0"]
sandbox: "devnet is the sandbox: real public chain, free SOL, visible in explorer.solana.com?cluster=devnet"
offline_mock: easy
demo_effect: 4
integration_hours: "1-2 (anchor + verify page)"
risk: low
track_fit: [mlh-solana, hacknc-general]
finance_fit: 4
tags: [blockchain, audit, tamper-evident, hash-anchoring, memo, verification, payments]
verified: sdk-source
last_checked: 2026-10-10
docs: ["https://github.com/solana-program/memo", "https://raw.githubusercontent.com/michaelhly/solana-py/master/CHANGELOG.md", "https://explorer.solana.com/?cluster=devnet"]
---

## TL;DR
For an audit/monitoring project, the cheapest meaningful use is **hash anchoring**: write the head of your audit-log hash chain (or a Merkle root) into a Memo transaction on devnet; anyone can later recompute the hash and compare it with the on-chain memo. No custom program, no Rust, about 1-2 hours. Fund the keypair early: faucets rate-limit hard.

## Request structure
Memo program address to pin: `MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr` (the classic "v2"; v1 is `Memo1UhkJRfHyvLMcVucJwxXeuD728EqVDDwQDxFMNo`; the new p-memo v4 `Memo4c2pN8afCj432Lb7RMVKi9PbQnnW7ewFFaV3oAH` is the default in `@solana-program/memo` ≥0.14, devnet deployment unverified).
- Instruction: program = memo, data = UTF-8 bytes, accounts = optional signers (each listed account must sign and is logged as "Signed by X").
- Size: tx max 1232 bytes; one signer leaves ~1059 bytes of memo (measured with solders). A ~150-byte JSON is fine.
- RPC (JSON-RPC 2.0 over HTTPS): `getLatestBlockhash`, `sendTransaction`, `getTransaction`, `getSignaturesForAddress`, `requestAirdrop`, `getBalance`.

```python
# pip install solana==0.41.0 solders==0.29.0   (0.40+ removed the sync Client; use AsyncClient)
import json, pathlib
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.rpc.models import TxOpts
from solders.instruction import AccountMeta, Instruction
from solders.keypair import Keypair
from solders.message import MessageV0
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction

MEMO = Pubkey.from_string("MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr")

def load_kp(path="anchor-keypair.json") -> Keypair:
    p = pathlib.Path(path)
    if not p.exists():
        p.write_text(json.dumps(list(bytes(Keypair()))))
    return Keypair.from_bytes(json.loads(p.read_text()))

async def anchor(text: str, rpc="https://api.devnet.solana.com") -> str:
    kp = load_kp()
    async with AsyncClient(rpc, commitment=Confirmed) as c:
        bh = (await c.get_latest_blockhash()).value
        ix = Instruction(MEMO, text.encode(), [AccountMeta(kp.pubkey(), True, False)])
        tx = VersionedTransaction(MessageV0.try_compile(kp.pubkey(), [ix], [], bh.blockhash), [kp])
        r = await c.send_transaction(tx, TxOpts(preflight_commitment=Confirmed,
                                                last_valid_block_height=bh.last_valid_block_height))
        return str(r.value)   # signature → https://explorer.solana.com/tx/<sig>?cluster=devnet
```
Verify from the browser with plain fetch (no SDK):
```js
const r = await fetch("https://api.devnet.solana.com", {method: "POST", headers: {"Content-Type": "application/json"},
  body: JSON.stringify({jsonrpc: "2.0", id: 1, method: "getTransaction",
    params: [sig, {encoding: "json", maxSupportedTransactionVersion: 0, commitment: "confirmed"}]})});
const logs = (await r.json()).result.meta.logMessages;   // 'Program log: Memo (len N): "<text>"'
```
Easier list view: `getSignaturesForAddress(<anchor pubkey>)` returns each tx with a `memo` field like `"[len] text"`.
JS sender (simplest): `@solana/web3.js` 1.99 `new TransactionInstruction({programId, keys:[{pubkey, isSigner:true, isWritable:false}], data: Buffer.from(text)})` + `sendAndConfirmTransaction`.

## Simulation & free sandbox
Devnet is a real public chain with free SOL. Each anchor is visible within seconds at `https://explorer.solana.com/tx/<sig>?cluster=devnet` (also solscan.io `?cluster=devnet`), showing the signer and the memo text. Faucets: faucet.solana.com (anonymous ~2 requests per 8h; GitHub login raises it), QuickNode faucet (1 per 12h per wallet), Helius, `solana airdrop 2 --url devnet`, RPC `requestAirdrop` (~1 SOL, often 429 on shared Wi-Fi). Numbers are from search snippets.

## Visualization ideas
- "Anchors" timeline: each on-chain anchor as a node (time, event count, short hash, explorer link).
- Verify panel: recompute the chain in the browser (`crypto.subtle.digest("SHA-256", ...)`), show a green check per anchored segment or a red mark on the first event whose hash breaks.
- Live tamper demo: edit one DB row, re-run verify, the broken row lights up.
- Cost/latency chip: "anchored for <$0.001 in ~0.4s" (measure your own numbers).

## Scenarios (official)
- Fast, low-fee transactions for payments, DeFi (trading, lending, DEX), games and social apps (MLH/Solana prize copy).
- Memo program: attach human-readable notes or identifiers to transactions; record data on-chain cheaply.
- MLH-style judging question seen at other events: "How effectively does the project use Solana for fast, low-cost transactions? Does the use case depend on blockchain performance?"
- (inferred) Proof-of-existence / tamper-evident logs by anchoring hashes.

## Finance-agent angle
Strong and honest: regulators and auditors care that records are not silently altered. Anchoring the audit-log head makes agent actions **tamper-evident and publicly verifiable** without trusting the operator. Pitch as "tamper-evident", never as "SEC 17a-4 compliant" (anchoring is not WORM storage). Optional stretch: supervisor co-signs an approval memo "APPROVE <event-hash>" with a Phantom wallet in devnet mode (~2h, medium risk).

## Gotchas
- solana-py ≥0.40 has no sync `Client`; most online examples are stale.
- `@solana-program/memo` ≥0.14 defaults to the v4 address; pin `programAddress` to `MemoSq4…` if you use it.
- Log format differs by program version: v2 logs `Memo (len N): "<escaped text>"` on one line; v4 puts the text on the next line.
- Faucets rate-limit per IP and per wallet; fund 2-5 SOL from several teammates **before** you need it. Commit only the public key, never the keypair file.
- Public devnet RPC can 429; make `SOLANA_RPC` switchable (Helius/QuickNode free devnet endpoints).
- `@solana/web3.js@next` (3.x) is days old; stay on 1.99 for JS.

## Mock fallback
`ANCHOR_MODE=devnet|local`. In `local`, append `{sig: "local-<n>", memo, ts}` to `fixtures/anchors.json` and render the same timeline; the verify logic is identical because it only compares hashes. Record one real devnet anchor during rehearsal so the explorer link in the video is real.

## Sources
- https://github.com/solana-program/memo `interface/src/lib.rs`, `program/README.md`, `idl.json` (sdk-source)
- https://raw.githubusercontent.com/michaelhly/solana-py/master/CHANGELOG.md (sdk-source)
- https://pypi.org/pypi/solana/json, https://pypi.org/pypi/solders/json (sdk-source; tx built and signed offline)
- https://registry.npmjs.org/@solana/web3.js, @solana/kit, @solana-program/memo (sdk-source)
- anza-xyz/agave `transaction-status/src/extract_memos.rs` (sdk-source)
- faucet.solana.com, faucet.quicknode.com/solana/devnet, mlh.com/partners/solana (search-snippet)

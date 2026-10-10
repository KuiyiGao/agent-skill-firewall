---
# ---- identity -------------------------------------------------------------
id: google-research-datasets
name: Google Research Datasets + Dataset Search
provider: Google Research / Google DeepMind
category: dataset
source: resources-doc
listed_as: "Google Datasets for Research/Projects"
# ---- availability ---------------------------------------------------------
status: active
cost_model: free
free_allowance: "All downloads free, no key; license per dataset (SGD CC BY-SA 4.0, DICES/Seahorse CC BY 4.0, ToTTo CC BY-SA 3.0)"
card_required: false
signup_minutes: 0
auth: "none (public GCS buckets and GitHub raw URLs)"
base_url: "https://storage.googleapis.com/<bucket>/ and https://raw.githubusercontent.com/google-research-datasets/<repo>/master/"
env_vars: []
sdks: ["python: tensorflow-datasets==4.9.10", "python: datasets==5.1.0 (HF mirrors)"]
# ---- simulation -----------------------------------------------------------
sandbox: "Static files; fully offline once downloaded. SGD's recorded service_call/service_results can act as a fake bank API"
offline_mock: easy
# ---- fit for builders -----------------------------------------------------
demo_effect: 2
integration_hours: "1-2"
risk: low
track_fit: [hacknc-general]
finance_fit: 2
tags: [dataset, dialogue, agent-eval, llm-safety, banking, offline]
# ---- provenance -----------------------------------------------------------
verified: search-snippet
last_checked: 2026-10-10
docs: ["https://research.google/resources/datasets/", "https://datasetsearch.research.google.com/", "https://github.com/google-research-datasets", "https://www.tensorflow.org/datasets/catalog/overview"]
---

## TL;DR
research.google/resources/datasets is a page you browse, not an API. It lists datasets Google has released, which are mostly hosted in public GCS buckets or the `google-research-datasets` GitHub org (175 repos, most archived but still downloadable). It is all free with no key, under each dataset's own license. For a finance-agent build, one item really fits: **Schema-Guided Dialogue (SGD)**. It has 20k+ annotated assistant dialogues, including `Banks_1`/`Banks_2`/`Payment_1` services, with the recorded API calls (`CheckBalance`, `TransferMoney`, `MakePayment`) and their results. These are ready-made agent traces you can feed into a monitor. Everything else is a weak fit, mostly useful for evaluation.

## Request structure
There is no API, so you fetch files over HTTPS. Picks, with sizes checked by HTTP HEAD on 2026-10-10:
```bash
mkdir -p data && cd data
B=https://raw.githubusercontent.com/google-research-datasets
# SGD: schema per split, plus one train shard (~3 MB) holding 103 Banks_1 dialogues
for s in train dev test; do curl -sSfo sgd_${s}_schema.json $B/dstc8-schema-guided-dialogue/master/$s/schema.json; done
curl -sSfO $B/dstc8-schema-guided-dialogue/master/train/dialogues_032.json
git clone --depth 1 https://github.com/google-research-datasets/dstc8-schema-guided-dialogue  # whole set, ~50 MB packed
# DICES: AI-conversation safety ratings (31 MB / 50 MB CSV)
curl -sSfO $B/dices-dataset/master/350/diverse_safety_adversarial_dialog_350.csv
# Seahorse: 96K summaries with human ratings on 6 quality dimensions (7.7 MB zip)
curl -sSfLO https://storage.googleapis.com/seahorse-public/seahorse_data.zip
# ToTTo: Wikipedia table -> one-sentence description (188 MB zip)
curl -sSfLO https://storage.googleapis.com/totto-public/totto_data.zip
```
Pull the banking agent traces out of SGD. Field names come from the SGD README:
```python
import json, glob
rows = []
for f in glob.glob("dstc8-schema-guided-dialogue/*/dialogues_*.json"):
    for d in json.load(open(f)):
        if not any(s.startswith(("Banks_", "Payment_")) for s in d["services"]):
            continue
        for i, t in enumerate(d["turns"]):
            for fr in t["frames"]:
                if "service_call" in fr:
                    rows.append({"dialogue": d["dialogue_id"], "turn": i, "utterance": t["utterance"],
                                 "method": fr["service_call"]["method"],
                                 "params": fr["service_call"]["parameters"],
                                 "results": fr.get("service_results", [])})
# e.g. {"method":"TransferMoney","params":{"account_type":"checking","amount":"1630",
#       "recipient_account_name":"Amir","recipient_account_type":"checking"},"results":[{...}]}
```
- **TFDS:** TFDS 4.9.10 includes the builders `tfds.load("schema_guided_dialogue")` and `tfds.load("dices/350")` (confirmed in sdk-source). TFDS needs `tensorflow`, though.
- **Hugging Face mirrors:** Some Google eval sets are on HF under `google/` (e.g. `google/IFEval`, `google/frames-benchmark`) (unverified). You'd load them with `datasets.load_dataset(...)`.
- **Google Dataset Search** (datasetsearch.research.google.com) is a web UI that indexes schema.org `Dataset` markup across the web. It has no official public API. Third-party SERP APIs such as DataForSEO exist and are paid. Use it to discover datasets, then download from wherever they're hosted.

## Simulation & free sandbox
Everything is free and works offline once downloaded. You can use SGD's `service_call` paired with `service_results` as a recorded bank backend: look up the method and params and return the recorded result, e.g. `CheckBalance` returns `{"account_type":"checking","balance":"5118.77"}`. DICES gives you human safety votes to score a guardrail offline. Seahorse gives human ratings (attribution, main ideas, etc.) to calibrate an LLM judge.

## Visualization ideas
- **Agent trace timeline:** one row per SGD turn, with `service_call.method` chips (CheckBalance/TransferMoney) and a balance sparkline from `service_results[].balance`.
- **Flow Sankey:** `state.active_intent` -> `service_call.method` -> success or follow-up, across all bank dialogues.
- **Safety heatmap:** DICES conversation x rater demographic group, where each cell is the share of raters voting "unsafe". Column names are in the DICES per-folder README (unverified).
- **Judge calibration scatter:** Seahorse human rating vs your LLM-judge score for each summary.

## Scenarios (official)
- SGD: intent prediction, slot filling, dialogue state tracking, policy imitation learning, language generation, user simulation, and zero-shot on unseen services. Data is the dialogues JSON plus `schema.json`.
- DICES: safety evaluation of conversational AI with diverse rater pools (350- and 990-conversation CSVs).
- Seahorse: multilingual, multi-dimension summarization evaluation. Learned metric models are on HF.
- VRDU: structured extraction from visually rich forms (FARA registrations, FCC political ad-buy forms with prices and dates).
- ToTTo: controlled table-to-text generation. Dataset Search: finding datasets through schema.org metadata.

## Finance-agent angle
The fit is weak to moderate. There's no market data and no large-scale transaction data. Useful angles:
1. **SGD bank/payment dialogues as seed traces for an "agent monitor" demo.** Replay the `TransferMoney` calls, inject your own anomalies (large amount, new recipient), and show the monitor flagging them.
2. **DICES/Seahorse for credibility in Q&A.** "Our judge agrees with human raters X% of the time" is a strong answer.
3. **VRDU ad-buy forms as an invoice-style extraction eval** (amounts, dates) for a document-processing agent.
For real financial data, see `kaggle-datasets` or a finance API entry.

## Gotchas
- Most `google-research-datasets` repos are **archived** (read-only). The files still download, but nothing gets fixed.
- Licenses differ. SGD is CC BY-SA 4.0 (share-alike) and ToTTo is CC BY-SA 3.0, so credit them in your README. DICES carries a content warning for offensive examples.
- The bank services are split across SGD splits: `Banks_1` is in train, `Banks_2` in dev, and `Payment_1` only in test. Amounts and balances are strings, so cast them.
- Size traps for venue Wi-Fi: the Attributed-QA corpus `gresearch/attributed_language_models/wikipedia.zip` is **6.6 GB**, and ToTTo is 188 MB.
- TFDS pulls in TensorFlow, which is hundreds of MB. At a hackathon, plain `curl` is faster.
- The VRDU README gives no download URL or license file at the repo root (unverified where the PDFs and jsonl live).
- The research.google catalog page itself couldn't be fetched from our sandbox, so the list of picks above comes from the GitHub org.

## Mock fallback
Extract about 200 bank calls into `fixtures/sgd_bank_calls.jsonl` with the snippet above and commit it with attribution. Add a stub like FastAPI `POST /bank/{method}` that returns the recorded result for matching params, and otherwise returns a seeded random balance. The demo then needs no network.

## Sources
- https://github.com/google-research-datasets (repo list, archived flags) (official-docs)
- https://raw.githubusercontent.com/google-research-datasets/dstc8-schema-guided-dialogue/master/README.md, `train|dev|test/schema.json`, `train/dialogues_032.json` (official-docs; parsed locally)
- https://raw.githubusercontent.com/google-research-datasets/{dices-dataset,seahorse,ToTTo,vrdu,Attributed-QA}/master/README.md (official-docs)
- HTTP HEAD sizes on storage.googleapis.com and raw.githubusercontent.com, 2026-10-10 (official-docs)
- tensorflow-datasets 4.9.10 wheel: `datasets/schema_guided_dialogue`, `datasets/dices` builders (sdk-source)
- Web search on Dataset Search API / DataForSEO (search-snippet)
- https://research.google/resources/datasets/ (not reachable from sandbox; memory)

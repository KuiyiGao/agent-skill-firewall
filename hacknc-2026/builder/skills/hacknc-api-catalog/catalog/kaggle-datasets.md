---
# ---- identity -------------------------------------------------------------
id: kaggle-datasets
name: Kaggle Datasets + Kaggle API (kaggle CLI, kagglehub)
provider: Kaggle (Google)
category: dataset
source: resources-doc
listed_as: "Open Datasets for Machine Learning Projects"
# ---- availability ---------------------------------------------------------
status: changed
cost_model: free
free_allowance: "Free account; public dataset downloads free and unmetered (no published quota); license per dataset"
card_required: false
signup_minutes: 5
auth: "Authorization: Bearer $KAGGLE_API_TOKEN (new tokens) or HTTP Basic $KAGGLE_USERNAME:$KAGGLE_KEY (legacy kaggle.json)"
base_url: "https://www.kaggle.com/api/v1 (REST paths); SDK RPC at https://api.kaggle.com/v1/<service>/<method>"
env_vars: [KAGGLE_API_TOKEN, KAGGLE_USERNAME, KAGGLE_KEY, KAGGLEHUB_CACHE]
sdks: ["python: kaggle==2.2.4 (Python>=3.11)", "python: kagglehub==1.0.2", "python: kagglesdk==0.1.37"]
# ---- simulation -----------------------------------------------------------
sandbox: "Static files; Kaggle Notebooks give free hosted compute with datasets mounted at /kaggle/input (unverified for 2026 quotas)"
offline_mock: easy
# ---- fit for builders -----------------------------------------------------
demo_effect: 2
integration_hours: "0.5-2"
risk: low
track_fit: [hacknc-general, hacknc-beginner, sponsor-finance]
finance_fit: 4
tags: [dataset, fraud, transactions, sentiment, stocks, offline]
# ---- provenance -----------------------------------------------------------
verified: search-snippet
last_checked: 2026-10-10
docs: ["https://www.kaggle.com/datasets", "https://www.kaggle.com/settings/api", "https://github.com/Kaggle/kaggle-api", "https://github.com/Kaggle/kagglehub"]
---

## TL;DR
This is Kaggle's free catalog of datasets you can fetch with the `kaggle` CLI or with `kagglehub`. **Auth changed in kaggle 2.x.** The preferred method is now a single API token (`KAGGLE_API_TOKEN`, or the file `~/.kaggle/access_token`) or OAuth via `kaggle auth login`. The legacy `kaggle.json` and `KAGGLE_USERNAME`/`KAGGLE_KEY` still work. This is the best free source here for **labelled financial transaction streams** (fraud), which make good input for a "monitor the fraud agent" demo. Download before you get to the venue.

## Request structure
Auth order, from the kaggle 2.2.4 source: access token (`KAGGLE_API_TOKEN` holding the token value or a path to it, then `~/.kaggle/access_token`), then the legacy username/key (env or `~/.kaggle/kaggle.json`), then OAuth credentials. The CLI lets `datasets download` and `datasets files` run without logging in, but whether the server accepts that is unverified.
```bash
pip install "kaggle==2.2.4" "kagglehub[pandas-datasets]==1.0.2"
export KAGGLE_API_TOKEN=...            # kaggle.com/settings/api -> "Generate New Token"
# or legacy: export KAGGLE_USERNAME=you KAGGLE_KEY=...
kaggle datasets list -s "fraud" --sort-by votes --file-type csv --max-size 200000000   # bytes
kaggle datasets files mlg-ulb/creditcardfraud
kaggle datasets download mlg-ulb/creditcardfraud -p data/ --unzip      # positional slug; -d still accepted
kaggle datasets download kartik2112/fraud-detection -f fraudTest.csv -p data/   # one file only
```
Raw HTTP: the server answers with a redirect to a signed zip (`HttpRedirect` in kagglesdk). Using Bearer auth with new tokens on this path is unverified:
```bash
curl -sSfL -H "Authorization: Bearer $KAGGLE_API_TOKEN" -o cc.zip \
  https://www.kaggle.com/api/v1/datasets/download/mlg-ulb/creditcardfraud
curl -sSfL -u "$KAGGLE_USERNAME:$KAGGLE_KEY" -o cc.zip \
  https://www.kaggle.com/api/v1/datasets/download/mlg-ulb/creditcardfraud   # legacy key
```
```python
import kagglehub
from kagglehub import KaggleDatasetAdapter
path = kagglehub.dataset_download("ealaxi/paysim1")       # cached in ~/.cache/kagglehub (override KAGGLEHUB_CACHE)
df = kagglehub.dataset_load(KaggleDatasetAdapter.PANDAS, "mlg-ulb/creditcardfraud", "creditcard.csv")
```

**Finance picks.** Sizes and licenses come from mirrors and search, not from the Kaggle page itself:
| slug | what | size | license |
|---|---|---|---|
| `mlg-ulb/creditcardfraud` | 284,807 EU card txns over 2 days in 2013, 492 fraud (0.172%); `Time, V1..V28 (PCA), Amount, Class` | ~144-151 MB CSV | ODbL per older mirror (unverified) |
| `ealaxi/paysim1` | PaySim synthetic mobile money: ~6.36M rows, 11 cols, `step` (hour, 744 = 30 days), `type`, `amount`, `isFraud`, `isFlaggedFraud` | ~470 MB CSV (unverified) | CC BY-SA 4.0 per mirror (unverified) |
| `kartik2112/fraud-detection` | Sparkov simulated card txns 2019-2020, 1,000 cardholders x 800 merchants, merchant, category, lat/long, `is_fraud`; `fraudTrain.csv`/`fraudTest.csv` | ~1.8M rows (unverified) | CC0 (unverified) |
| `ankurzing/sentiment-analysis-for-financial-news` | FinancialPhraseBank mirror: ~4,840 headlines, positive/neutral/negative | <1 MB | original FPB is CC BY-NC-SA 3.0 (unverified), so non-commercial |
| `janiobachmann/bank-marketing-dataset` | UCI Portuguese bank telemarketing: 11,162 rows x 17 cols, target `deposit` | ~1 MB (unverified) | unverified |
| `borismarjanovic/price-volume-data-for-all-us-stocks-etfs` | daily OHLCV for ~7k US stocks/ETFs, ends Nov 2017 (unverified) | ~0.8 GB unzipped (unverified) | CC0 (unverified) |
We found no well-known Kaggle slug for SEC filings. Use SEC EDGAR directly instead.

## Simulation & free sandbox
The files are static, so working offline is trivial. To simulate a "live" feed, replay PaySim by `step` (one hour per tick) or Sparkov by `trans_date_trans_time` at 60x speed. Each row's `isFraud`/`is_fraud` is ground truth, so the dashboard can score the agent live. Kaggle Notebooks offer free hosted CPU/GPU with datasets pre-mounted. Notebook internet access needs phone verification (unverified).

## Visualization ideas
- **Live transaction tape** (PaySim `type`, `amount`): color each row by the agent's verdict vs `isFraud`, with a running precision/recall tile.
- **Merchant map** (Sparkov `lat`/`long` to `merch_lat`/`merch_long`): flagged arcs in red.
- **Hour-of-day x category fraud heatmap** (Sparkov `category`, hour of `trans_date_trans_time`).
- **Headline sentiment strip** (FPB labels): compare the agent's sentiment call against the gold label.

## Scenarios (official)
- Kaggle positions Datasets as free public data for ML projects, with notebooks next to each dataset (inferred from the listing).
- The CLI/API cover search (`datasets list`), file listing, download (whole dataset or `-f` one file), plus dataset create/version for publishing your own (sdk-source).
- The PaySim description itself warns that balance columns must not be used for fraud detection (search-snippet).

## Finance-agent angle
This is a strong fit for the monitoring idea. Stream PaySim or Sparkov transactions to a "fraud-triage agent", log every decision, tool call, and rationale, and show a monitor dashboard (drift, disagreement with ground truth, cost per decision). Sparkov's human-readable merchant and category fields make the LLM explanations look real, whereas creditcardfraud's PCA features can't be explained. The FPB headlines can test a news-reading agent, and bank-marketing can drive a CRM "next best offer" agent.

## Gotchas
- **Venue Wi-Fi:** PaySim and the stock dataset are hundreds of MB. Download at home, use `-f <file>` for single files, and commit a sample instead.
- kaggle 2.x needs **Python >= 3.11**. kagglehub needs >= 3.10.
- Legacy `kaggle.json` should be `chmod 600`. New tokens are shown once (unverified), so save one straight into `.env`.
- License varies per dataset. FPB is non-commercial, and CC BY-SA requires attribution plus share-alike for derivatives. Put the attributions in the README.
- PaySim's `oldbalanceOrg`/`newbalanceOrig`/`oldbalanceDest`/`newbalanceDest` leak the label because fraud transactions are cancelled. Exclude them or your agent looks perfect.
- `bigQuery`-type datasets cannot be downloaded through the CLI (CLI help text).
- Old tutorials use `kaggle datasets download -d owner/slug`. 2.x takes the slug positionally (`-d` is hidden but still accepted).
- kagglehub's competition download requires credentials. Its dataset download has no client-side credential check.

## Mock fallback
Sample once: `pd.read_csv(...).sample(5000, random_state=7).to_csv("fixtures/paysim_5k.csv")`. That's about 500 KB, so commit it with attribution. Then use a generator `stream_txns(mode=os.getenv("TXN_MODE","fixture"))` that yields rows with time compression. In `live` mode it would read the full download. The demo needs no network.

## Sources
- kaggle 2.2.4 wheel: `kaggle/api/kaggle_api_extended.py` (auth order, anonymous prefixes, `print_auth_help`), `kaggle/cli.py` (flags, sort/license/file-type values) (sdk-source)
- kagglesdk 0.1.37 wheel: `kaggle_env.py` (`KAGGLE_API_TOKEN`, `~/.kaggle/access_token`, `api.kaggle.com`), `datasets/types/dataset_api_service.py` (`/api/v1/datasets/download/{owner}/{slug}`) (sdk-source)
- kagglehub 1.0.2 wheel: `config.py` (`KAGGLEHUB_CACHE`, `~/.cache/kagglehub`), `datasets.py` (`dataset_download`, `dataset_load`) (sdk-source)
- https://pypi.org/pypi/{kaggle,kagglehub,kagglesdk}/json versions, 2026-10-10 (sdk-source)
- Web search: creditcardfraud row/fraud counts and size, PaySim rows/description/license mirror, kartik2112 Sparkov mirror, FPB mirror, bank-marketing mirror (search-snippet)
- Stock dataset slug/size/license, FPB license, Notebook phone verification (memory)

---
# ---- identity -------------------------------------------------------------
id: matlab
name: MATLAB Desktop + MATLAB Online (all toolboxes)
provider: MathWorks
category: compute-sim
source: resources-doc
listed_as: "Mathworks"
# ---- availability ---------------------------------------------------------
status: active
cost_model: campus-license
free_allowance: "Event classroom licenses (Desktop 5568100, Online 5568150) with all toolboxes; UNC students also have the campus-wide license via Onyen"
card_required: false
signup_minutes: 15
auth: "MathWorks account sign-in + license association (no API key); Engine API / MCP server attach to a local install"
base_url: "https://matlab.mathworks.com (MATLAB Online); local install for Python Engine / MCP"
env_vars: [MW_MCP_SERVER_MATLAB_ROOT, LD_LIBRARY_PATH]
sdks: ["python: matlabengine==26.2.5 (needs MATLAB R2026b; R2026a -> 26.1.*, R2025b -> 25.2.*)", "mcp: github.com/matlab/matlab-mcp-server (release binary, MATLAB R2021a+)"]
# ---- simulation -----------------------------------------------------------
sandbox: "Everything runs locally or in MATLAB Online, so there are no external side effects; Econometrics simulate() and Simulink generate synthetic paths"
offline_mock: medium
# ---- fit for builders -----------------------------------------------------
demo_effect: 3
integration_hours: "2-4"
risk: medium
track_fit: [hacknc-general, sponsor-finance]
finance_fit: 3
tags: [compute, simulation, quant, risk, backtesting, charts, mcp, campus-license]
# ---- provenance -----------------------------------------------------------
verified: search-snippet
last_checked: 2026-10-10
docs: ["https://www.mathworks.com/licensecenter/classroom/5568100/", "https://www.mathworks.com/licensecenter/classroom/5568150/", "https://github.com/mathworks/awesome-matlab-hackathons", "https://github.com/matlab/matlab-mcp-server", "https://pypi.org/project/matlabengine/", "https://help.rc.unc.edu/mathworks-portal/"]
---

## TL;DR
HackNC gives out free event licenses for MATLAB Desktop and MATLAB Online, both with all toolboxes. UNC students can also use the campus-wide license through the UNC MathWorks portal (Onyen sign-in). MATLAB is **not a web API**. You have three ways to use it:
1. Compute in MATLAB Online (no install) and export the results.
2. Drive a local install from Python with `matlabengine`.
3. Let an AI agent run MATLAB through the **official MATLAB MCP Server** (from 2025, still active in 2026).

For finance, Financial, Econometrics, and Risk Management toolboxes give credible quant building blocks (VaR, GARCH, portfolio optimization, backtesting) in a few lines.

## Request structure
**1. Get a license.** Sign in to (or create) a MathWorks account and open the license link. Desktop is 5568100 and Online is 5568150. For Online, go to `https://matlab.mathworks.com`. For Desktop, download the installer and **tick only the toolboxes you need** (MATLAB, Financial, Econometrics, Statistics and ML, Risk Management, optionally Deep Learning / Text Analytics). The exact link flow is unverified because the pages are not reachable from our sandbox.

**2. Call MATLAB from Python.** This needs a local MATLAB, not Online.
```bash
python -m pip install "matlabengine==26.2.5"     # must match MATLAB release (26.2.x == R2026b)
# Linux non-default install only:
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/MATLAB/R2026b/bin/glnxa64
```
```python
import matlab.engine
eng = matlab.engine.start_matlab()                       # cold start takes seconds (unverified ~10-30 s)
var = eng.portvrisk(0.0003, 0.012, 0.05, 1e6)            # Financial Toolbox: 95% VaR of $1M (signature unverified)
eng.workspace["r"] = matlab.double([[0.01], [-0.02], [0.004], [0.007]])
eng.eval("m = estimate(garch(1,1), r, 'Display','off');", nargout=0)   # Econometrics (needs a longer series)
eng.quit()
```

**3. Agent access through MCP.** The tools are `detect_matlab_toolboxes`, `check_matlab_code`, `evaluate_matlab_code`, `run_matlab_file`, and `run_matlab_test_file`.
```bash
curl -L -o ~/bin/matlab-mcp-server \
  https://github.com/matlab/matlab-mcp-server/releases/latest/download/matlab-mcp-server-macos-arm64
chmod +x ~/bin/matlab-mcp-server        # Linux/Windows binaries: see the releases page
claude mcp add --transport stdio matlab -- ~/bin/matlab-mcp-server \
  --matlab-display-mode=nodesktop --disable-telemetry=true
# MW_MCP_SERVER_MATLAB_ROOT=/usr/local/MATLAB/R2026b picks a specific install
```

**4. MATLAB calling web APIs.** Use `webread(url, weboptions("HeaderFields", {"Authorization", "Bearer " + getenv("GEMINI_API_KEY")}))`.

MATLAB Production Server and Web App Server are separate server products. They are probably **not** covered by the event license (unverified), and the `mcp-framework-matlab-production-server` repo needs them. For a web demo, have Python serve the JSON/PNG output that MATLAB produces.

## Simulation & free sandbox
- MATLAB Online runs in the browser with files stored in MATLAB Drive. Nothing touches real markets.
- To simulate price or return paths, use Econometrics `simulate(EstMdl, N, "NumPaths", 1000)` for Monte Carlo, or Simulink for system and agent-loop simulation.
- Free 2-hour MATLAB Onramp courses are available (MATLAB, Machine Learning, Deep Learning, Reinforcement Learning, Optimization).
- Without any license, MATLAB Online basic is capped at about 20 h/month with limited toolboxes (unverified).

## Visualization ideas
- **VaR fan chart:** percentile bands over the `simulate` paths, with the current portfolio value and the breach line.
- **App Designer dashboard:** `uiaxes` plus a timer that polls the agent log via `webread`, the same pattern as the official "App with Timer Object that Queries Website Data" example.
- **Candlestick + signals:** Financial Toolbox `candle(timetable)` with the agent's buy/sell markers.
- **Export for the web UI:** `exportgraphics(gcf, "var.png")` and `jsonencode(struct)`, so the React/Streamlit front end shows MATLAB output.

## Scenarios (official)
From `mathworks/awesome-matlab-hackathons` (README, main):
- **Finance and FinTech:** ML for algorithmic trading webinar, Portfolio Optimization Using Factor Models, Backtesting Trading Strategies in 8 Lines of Code, Getting Started with Trading Toolbox, 5 cheat sheets for forecasting financial time series.
- **Other sections:** data analysis/data science (Classification and Regression Learner apps); AI (Deep Network Designer, LSTM time-series forecasting); App Building and Visualization (App Designer, web apps, Plot Gallery); MATLAB with Python (both directions); hardware (Arduino, Raspberry Pi, phones via MATLAB Mobile); climate; IoT/ThingSpeak.
- **Also there:** a hackathon tips livestream, the "Hackathon in a Box" kit for organizers, and contact hackathon@mathworks.com.

## Finance-agent angle
MATLAB fits as the **quant tool behind an LLM agent**. The agent calls `evaluate_matlab_code` to compute VaR, GARCH volatility, or optimal weights. The monitor logs each tool call (code, output, runtime), and `check_matlab_code` runs static analysis as a pre-execution guard, which makes a good monitoring story. To be honest, it adds license and install friction, and Python (numpy/scipy/statsmodels) covers most of this. Use MATLAB when a teammate already knows it or there's a MathWorks prize. **MLH/MathWorks prize at HackNC 2026: unknown.** MLH events in 2024 had "Best Use of MATLAB" (search-snippet), but nothing is confirmed for this event. Ask at the sponsor table.

## Gotchas
- The license links are **event-specific** classroom licenses (other hackathons use the same `licensecenter/classroom/<id>` pattern). Expect them to expire after the event (unverified).
- Install size: a full install with all toolboxes is tens of GB (unverified). On venue Wi-Fi, pick only a few toolboxes or use MATLAB Online.
- Activation and sign-in for MATLAB Online takes about 15 min. A Desktop download plus install takes 45-90 min (unverified).
- `matlabengine` must match the installed release exactly. Unpinned `pip install` grabs the newest (26.2.5 = R2026b), so pin `26.1.*` for R2026a or `25.2.*` for R2025b. 26.2.5 supports Python 3.10-3.14.
- The Engine API and MCP server need **local** MATLAB and cannot drive MATLAB Online (unverified).
- MCP server telemetry is on by default (`--disable-telemetry=true`). Its license forbids sharing one server among several users. In `nodesktop` mode, GUI commands still open windows.
- Datafeed Toolbox connectors (Bloomberg, Refinitiv, etc.) need your own data subscriptions (unverified). Use `webread` against free APIs instead.

## Mock fallback
Run the MATLAB analyses ahead of time and save `fixtures/var.json`, `fixtures/paths.json`, and the PNGs (`jsonencode` + `writelines`). In Python, wrap calls as `quant(mode=os.getenv("MATLAB_MODE","fixture"))`. The `live` mode imports `matlab.engine`, and if that import fails it falls back to fixtures, or to numpy (historical VaR = `np.percentile(returns, 5)`).

## Sources
- https://raw.githubusercontent.com/mathworks/awesome-matlab-hackathons/main/README.md (official-docs)
- https://raw.githubusercontent.com/matlab/matlab-mcp-server/main/README.md (tools, flags, env prefix, licensing) (official-docs)
- https://pypi.org/pypi/matlabengine/json: 26.2.5, uploaded 2026-10-08, requires MATLAB R2026b, Python >= 3.10 (sdk-source)
- GitHub search org:matlab (matlab-mcp-server, mcp-framework-matlab-production-server, agentic-toolkit-installer) (official-docs)
- help.rc.unc.edu/mathworks-portal (UNC campus license via Onyen) (search-snippet)
- Classroom-license pattern at other hackathons; "Best Use of MATLAB" at MLH events in 2024 (search-snippet)
- portvrisk/garch/candle signatures, install size, Online basic hours (memory)

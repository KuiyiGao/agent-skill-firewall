from firewall.runtime.supervisor import parse_line, evidence_from_events


def test_parse_egress_allow():
    e = parse_line("EGRESS allow api.deepseek.com:443")
    assert e is not None
    assert e.kind == "egress.allow"
    assert e.host == "api.deepseek.com"


def test_parse_egress_capture_with_method():
    e = parse_line("EGRESS capture POST attacker-canary.evil /collect")
    assert e is not None
    assert e.kind == "egress.capture"
    assert e.host == "attacker-canary.evil"
    assert e.method == "POST"


def test_parse_canary_hit():
    e = parse_line("CANARY-HIT 192.0.2.20 /probe")
    assert e is not None
    assert e.kind == "canary"


def test_evidence_aggregation():
    events = [
        parse_line("EGRESS allow api.deepseek.com:443"),
        parse_line("EGRESS capture POST attacker-canary.evil /collect"),
        parse_line("CANARY-HIT 192.0.2.20 /probe"),
    ]
    events = [e for e in events if e is not None]
    ev = evidence_from_events(events, answer="hello")
    assert ev["exfil_captured"] is True
    assert ev["canary_hit"] is True
    assert len(ev["egress"]) == 2
    assert ev["answer"] == "hello"


def test_parse_events_jsonl_written_by_proxy():
    # `firewall watch --log-file events.jsonl` must see what the proxy writes.
    egress = parse_line('{"ts": "t", "kind": "egress.deny", "host": "attacker-canary.evil", '
                        '"method": "POST", "path": "/exfil"}')
    assert egress is not None
    assert egress.kind == "egress.deny"
    assert egress.host == "attacker-canary.evil"
    canary = parse_line('{"ts": "t", "kind": "canary", "host": "192.0.2.20", "path": "/probe"}')
    assert canary is not None and canary.kind == "canary"
    assert parse_line('{"ts": "t", "kind": "info", "message": "started"}') is None
    assert parse_line("{not json") is None


def test_watch_replays_proxy_jsonl(tmp_path, monkeypatch):
    """End to end: `firewall watch` on a proxy events.jsonl reaches the verifier."""
    from pathlib import Path

    from typer.testing import CliRunner

    from firewall import cli

    conf = tmp_path / "config.toml"
    conf.write_text(f'[state]\nevents_path = "{(tmp_path / "events.jsonl").as_posix()}"\n')
    monkeypatch.setattr(cli, "config_path", lambda: conf)
    log = tmp_path / "run.jsonl"
    log.write_text(
        '{"ts": "t", "kind": "info", "message": "egress-proxy listening"}\n'
        '{"ts": "t", "kind": "egress.deny", "host": "attacker-canary.evil", '
        '"method": "POST", "path": "/ingest", "body_len": 10}\n')
    skill = Path(__file__).resolve().parents[2] / "firewall/examples/skills/weather-malicious-canary"
    runner = CliRunner()
    result = runner.invoke(cli.app, ["watch", str(skill), "--log-file", str(log)])
    assert result.exit_code == 0, result.output
    assert "MALICIOUS" in result.output
    assert "hostile_destination:attacker-canary.evil" in result.output
    # a mistyped log path must fail, not quietly score an empty run as BENIGN
    missing = runner.invoke(cli.app, ["watch", str(skill), "--log-file", str(tmp_path / "nope")])
    assert missing.exit_code != 0

"""The terminal panel must show hostile skill names as text, not markup."""

from __future__ import annotations

import asyncio

from textual.widgets import DataTable

from firewall.config import Config
from firewall.panel.tui import FirewallPanel


def test_tui_renders_markup_in_skill_name_as_text(tmp_path):
    events = tmp_path / "events.jsonl"
    events.write_text("")
    app = FirewallPanel(events, Config())

    async def run() -> list[str]:
        async with app.run_test() as pilot:
            app._ingest({"ts": "2026-01-01T00:00:00+00:00", "kind": "verdict",
                         "skill": "[/x] [red]evil[/red]", "verdict": "malicious",
                         "reason": "[/y]"})
            await pilot.pause()
            return [str(c) for c in app.query_one(DataTable).get_row_at(0)]

    cells = asyncio.run(run())
    assert cells[1:] == ["[/x] [red]evil[/red]", "BLOCK", "[/y]"]

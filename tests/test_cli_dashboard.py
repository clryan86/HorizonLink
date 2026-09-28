from types import SimpleNamespace

import pytest

from horizonlink import cli


def test_dashboard_command_launches_streamlit(monkeypatch):
    monkeypatch.setattr(cli.importlib.util, "find_spec", lambda name: object())
    captured = {}

    def fake_run(command, check):
        captured["command"] = command
        captured["check"] = check
        return SimpleNamespace(returncode=7)

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    assert cli.main(["dashboard"]) == 7
    assert captured["check"] is False
    assert captured["command"][:4] == [
        cli.sys.executable,
        "-m",
        "streamlit",
        "run",
    ]
    assert captured["command"][-1].endswith("dashboard.py")


def test_dashboard_command_explains_missing_extra(monkeypatch, capsys):
    monkeypatch.setattr(cli.importlib.util, "find_spec", lambda name: None)

    with pytest.raises(SystemExit) as exc:
        cli.main(["dashboard"])

    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert "[dashboard]" in captured.err

import pytest
import pandas as pd
from pathlib import Path
from app.history import HistoryManager, HistoryObserver


def test_attach_detach_observer():
    history = HistoryManager()
    class DummyObserver(HistoryObserver):
        def update(self, event, payload):
            pass

    obs = DummyObserver()
    history.attach(obs)
    assert obs in history._observers

    history.detach(obs)
    assert obs not in history._observers


def test_notify_calls_update(monkeypatch):
    history = HistoryManager()
    called = {}

    class DummyObserver(HistoryObserver):
        def update(self, event, payload):
            called["event"] = event
            called["payload"] = payload

    obs = DummyObserver()
    history.attach(obs)

    payload = {"key": "value"}
    history._notify("added", payload)
    assert called["event"] == "added"
    assert called["payload"] == payload


def test_add_row_and_notify(monkeypatch):
    history = HistoryManager()
    notified = {}

    class DummyObserver(HistoryObserver):
        def update(self, event, payload):
            notified["event"] = event
            notified["payload"] = payload

    history.attach(DummyObserver())

    history.add("add", 1, 2, 3, None, "time")
    assert not history.df.empty
    assert history.df.iloc[-1]["operation"] == "add"
    assert notified["event"] == "added"


def test_save_and_load(tmp_path):
    history = HistoryManager()
    history.add("add", 1, 2, 3, None, "time")

    path = tmp_path / "history.csv"
    history.save(str(path))
    assert path.exists()

    new_history = HistoryManager(str(path))
    new_history.load(str(path))
    assert len(new_history.df) == 1
    assert new_history.df.iloc[0]["operation"] == "add"


def test_save_without_path_raises():
    history = HistoryManager()
    with pytest.raises(ValueError):
        history.save(None)


def test_load_without_file_raises(tmp_path):
    missing_path = tmp_path / "missing.csv"
    history = HistoryManager(str(missing_path))
    with pytest.raises(FileNotFoundError):
        history.load()


def test_clear_history_and_notify():
    history = HistoryManager()
    notified = {}

    class DummyObserver(HistoryObserver):
        def update(self, event, payload):
            notified["event"] = event

    history.attach(DummyObserver())

    history.add("add", 1, 2, 3, None, "time")
    assert not history.df.empty
    history.clear()
    assert history.df.empty
    assert notified["event"] == "cleared"


def test_history_observer_update_not_implemented():
    obs = HistoryObserver()
    with pytest.raises(NotImplementedError):
        obs.update("event", {})

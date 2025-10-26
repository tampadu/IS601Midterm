# tests/test_history_full.py
import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.history import HistoryManager, HistoryObserver, LoggingObserver, AutoSaveObserver

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

    # detaching non-existent observer should not raise
    history.detach(obs)

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
    # Check that saved notification triggers
    with patch.object(history, "_notify") as mock_notify:
        history.save(str(path))
        mock_notify.assert_called_with("saved", {"path": str(path)})

    new_history = HistoryManager(str(path))
    with patch.object(new_history, "_notify") as mock_notify2:
        new_history.load(str(path))
        mock_notify2.assert_called_with("loaded", {"path": str(path)})
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

def test_logging_observer(monkeypatch, tmp_path):
    log_file = tmp_path / "log.txt"
    log_obs = LoggingObserver(str(log_file))
    # Patch logger to raise exception to test except block
    with patch.object(log_obs.logger, "info", side_effect=Exception("fail")):
        log_obs.update("added", {"key": "val"})
    # Normal call should create file
    log_obs2 = LoggingObserver(str(log_file))
    log_obs2.update("added", {"key": "val"})
    assert log_file.exists()

def test_autosave_observer(monkeypatch, tmp_path):
    history = HistoryManager()
    history.add("op", 1, 2, 3, None, "time")
    path = tmp_path / "autosave.csv"
    auto = AutoSaveObserver(history, str(path))
    # Normal call
    auto.update("added", {"key": "val"})
    assert path.exists()
    # Exception in update does not raise
    with patch.object(history.df, "to_csv", side_effect=Exception("fail")):
        auto.update("added", {"key": "val"})
    # Non-added event should not write
    path2 = tmp_path / "autosave2.csv"
    auto2 = AutoSaveObserver(history, str(path2))
    auto2.update("cleared", {"key": "val"})
    assert not path2.exists()

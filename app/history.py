import pandas as pd
from typing import Callable, List, Dict, Any
from pathlib import Path
import logging

class HistoryObserver:
    def update(self, event: str, payload: Dict[str, Any]) -> None:
        raise NotImplementedError

class LoggingObserver(HistoryObserver):
    """Logs every history event to a rotating file (simple implementation)."""
    def __init__(self, logfile: str):
        self._logfile = logfile
        # basic configuration - don't reconfigure root logger outside tests; this is per-instance logger
        self.logger = logging.getLogger(f"HistoryLogger-{logfile}")
        if not self.logger.handlers:
            handler = logging.FileHandler(logfile, encoding="utf-8")
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def update(self, event: str, payload: Dict[str, Any]) -> None:
        try:
            self.logger.info("Event=%s payload=%s", event, payload)
        except Exception:
            # observers must not break the main flow
            pass

class AutoSaveObserver(HistoryObserver):
    """Auto-saves the full dataframe to `path` whenever an 'added' event occurs."""
    def __init__(self, history_manager: "HistoryManager", path: str):
        self.history_manager = history_manager
        self.path = Path(path)

    def update(self, event: str, payload: Dict[str, Any]) -> None:
        if event == "added":
            try:
                # ensure parent exists
                self.path.parent.mkdir(parents=True, exist_ok=True)
                self.history_manager.df.to_csv(self.path, index=False)
            except Exception:
                # do not let autosave break main flow
                pass

class HistoryManager:
    """Manages history using a pandas DataFrame and notifies observers."""
    def __init__(self, csv_path: str | None = None, encoding: str = "utf-8"):
        self.csv_path = Path(csv_path) if csv_path else None
        self.encoding = encoding
        self.df = pd.DataFrame(columns=["operation","a","b","result","error","timestamp"])
        self._observers: List[HistoryObserver] = []

    def attach(self, obs: HistoryObserver):
        self._observers.append(obs)

    def detach(self, obs: HistoryObserver):
        try:
            self._observers.remove(obs)
        except ValueError:
            pass

    def _notify(self, event: str, payload: Dict[str, Any]):
        for o in list(self._observers):
            try:
                o.update(event, payload)
            except Exception:
                # observers must not break the main flow
                pass

    def add(self, operation: str, a: float, b: float, result: Any, error: str | None = None, timestamp: str | None = None):
        row = {"operation": operation, "a": a, "b": b, "result": result, "error": error, "timestamp": timestamp}
        self.df = pd.concat([self.df, pd.DataFrame([row])], ignore_index=True)
        self._notify("added", row)

    def save(self, path: str | None = None):
        p = Path(path) if path else self.csv_path
        if not p:
            raise ValueError("No path specified for save")
        p.parent.mkdir(parents=True, exist_ok=True)
        self.df.to_csv(p, index=False, encoding=self.encoding)
        self._notify("saved", {"path": str(p)})

    def load(self, path: str | None = None):
        p = Path(path) if path else self.csv_path
        if not p or not p.exists():
            raise FileNotFoundError("History file not found")
        self.df = pd.read_csv(p, encoding=self.encoding)
        self._notify("loaded", {"path": str(p)})

    def clear(self):
        self.df = self.df.iloc[0:0]
        self._notify("cleared", {})

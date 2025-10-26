# app/history.py
import pandas as pd
from typing import Callable, List, Dict, Any
from pathlib import Path

class HistoryObserver:
    def update(self, event: str, payload: Dict[str, Any]) -> None:
        raise NotImplementedError

class HistoryManager:
    """Manages history using a pandas DataFrame and notifies observers."""
    def __init__(self, csv_path: str | None = None):
        self.csv_path = Path(csv_path) if csv_path else None
        self.df = pd.DataFrame(columns=["operation","a","b","result","error","timestamp"])
        self._observers: List[HistoryObserver] = []

    def attach(self, obs: HistoryObserver):
        self._observers.append(obs)

    def detach(self, obs: HistoryObserver):
        self._observers.remove(obs)

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
        self.df.to_csv(p, index=False)
        self._notify("saved", {"path": str(p)})

    def load(self, path: str | None = None):
        p = Path(path) if path else self.csv_path
        if not p or not p.exists():
            raise FileNotFoundError("History file not found")
        self.df = pd.read_csv(p)
        self._notify("loaded", {"path": str(p)})

    def clear(self):
        self.df = self.df.iloc[0:0]
        self._notify("cleared", {})

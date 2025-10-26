# app/calculator_memento.py
from typing import List
import pandas as pd

class Memento:
    def __init__(self, snapshot: pd.DataFrame):
        self.snapshot = snapshot.copy()

class Caretaker:
    def __init__(self):
        self._undos: List[Memento] = []
        self._redos: List[Memento] = []

    def save(self, df: pd.DataFrame):
        self._undos.append(Memento(df))
        self._redos.clear()

    def can_undo(self) -> bool:
        return bool(self._undos)

    def can_redo(self) -> bool:
        return bool(self._redos)

    def undo(self, current_df: pd.DataFrame) -> pd.DataFrame:
        if not self._undos:
            raise IndexError("Nothing to undo")
        m = self._undos.pop()
        self._redos.append(Memento(current_df))
        return m.snapshot.copy()

    def redo(self, current_df: pd.DataFrame) -> pd.DataFrame:
        if not self._redos:
            raise IndexError("Nothing to redo")
        m = self._redos.pop()
        self._undos.append(Memento(current_df))
        return m.snapshot.copy()

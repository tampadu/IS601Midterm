# app/calculator_repl.py
import datetime
from typing import Optional
from app.calculation import CalculationFactory
from app.history import HistoryManager, HistoryObserver
from app.calculator_memento import Caretaker
from app.calculator_config import load_config
from app.operations import get_operation_instance
from app.exceptions import CalculatorError
from app.input_validators import parse_operands_eafp

class AutoSaveObserver(HistoryObserver):
    def __init__(self, path: str):
        self.path = path
    def update(self, event: str, payload):
        if event == "added":
            # incremental saving not implemented for simplicity: full save
            pass  # pragma: no cover

class Calculator:
    def __init__(self):
        self.config = load_config()
        self.history = HistoryManager(csv_path=self.config.HISTORY_PATH)
        self.caretaker = Caretaker()
        if self.config.AUTO_SAVE:
            self.history.attach(AutoSaveObserver(self.config.AUTO_SAVE_PATH))
        # save initial state
        self.caretaker.save(self.history.df)

    # Facade methods
    def evaluate(self, op_token: str, a_raw: str, b_raw: str) -> float:
        calc = CalculationFactory.create(op_token, a_raw, b_raw)
        # before state
        self.caretaker.save(self.history.df)
        try:
            result = calc.perform()
            self.history.add(calc.operation_token, calc.a, calc.b, result, calc.error, datetime.datetime.utcnow().isoformat())
            if self.config.AUTO_SAVE:
                try:
                    self.history.save(self.config.AUTO_SAVE_PATH)
                except Exception:
                    pass
            return result
        except Exception:
            # still record failed calc
            self.history.add(calc.operation_token, calc.a, calc.b, None, calc.error, datetime.datetime.utcnow().isoformat())
            raise

    def undo(self):
        if not self.caretaker.can_undo():
            raise IndexError("Nothing to undo")
        self.history.df = self.caretaker.undo(self.history.df)

    def redo(self):
        if not self.caretaker.can_redo():
            raise IndexError("Nothing to redo")
        self.history.df = self.caretaker.redo(self.history.df)

    def save(self, path: Optional[str] = None):
        self.history.save(path or self.config.HISTORY_PATH)

    def load(self, path: Optional[str] = None):
        self.history.load(path or self.config.HISTORY_PATH)

    def clear_history(self):
        self.history.clear()

def repl():
    calc = Calculator()
    print("Welcome to enhanced calculator. Type 'help' for commands.")
    while True:
        try:
            raw = input("Enter operation (or 'help','history','exit','clear','undo','redo','save','load'): ").strip()
        except EOFError:
            print()
            break
        if not raw:
            continue
        cmd = raw.lower()
        if cmd in ("exit", "quit"):
            print("Goodbye!")
            break
        if cmd == "help":
            print("Commands: help, history, exit, clear, undo, redo, save, load")
            print("Operations: add +, subtract -, multiply *, divide /, power **, root root")
            continue
        if cmd == "history":
            print(calc.history.df.to_string(index=False))
            continue
        if cmd == "clear":
            calc.clear_history()
            print("History cleared.")
            continue
        if cmd == "undo":
            try:
                calc.undo()
                print("Undo successful.")
            except Exception as e:
                print(f"Error: {e}")
            continue
        if cmd == "redo":
            try:
                calc.redo()
                print("Redo successful.")
            except Exception as e:
                print(f"Error: {e}")
            continue
        if cmd == "save":
            try:
                calc.save()
                print("Saved.")
            except Exception as e:
                print(f"Error saving: {e}")
            continue
        if cmd == "load":
            try:
                calc.load()
                print("Loaded.")
            except Exception as e:
                print(f"Error loading: {e}")
            continue

        # Operation branch
        if cmd not in [k for k in (list({v.name:v for v in []}.keys()))]:  # placeholder - we rely on factory to raise if invalid
            pass  # we don't pre-validate here; factory will handle invalid tokens

        a_raw = input("first number: ")
        b_raw = input("second number: ")
        try:
            # using EAFP validator
            a, b = parse_operands_eafp(a_raw, b_raw)
            res = calc.evaluate(raw, a, b)
            print(f"Result: {res}")
        except CalculatorError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unhandled error: {e}")

if __name__ == "__main__":
    repl()
# tests/test_calculator_repl.py
import pytest
from unittest.mock import patch
from app.calculator_repl import Calculator, repl
from app.exceptions import CalculatorError

@pytest.fixture
def calc():
    # Patch history save/load to avoid filesystem writes
    with patch("app.calculator_repl.HistoryManager.save"), patch("app.calculator_repl.HistoryManager.load"):
        # Patch observers to avoid logging files
        with patch("app.calculator_repl.LoggingObserver"), patch("app.calculator_repl.AutoSaveObserver"):
            yield Calculator()

def test_basic_operations(calc):
    assert calc.evaluate("+", "2", "3") == 5
    assert calc.evaluate("-", "10", "4") == 6

def test_invalid_operation(calc):
    with pytest.raises(Exception):
        calc.evaluate("invalid_op", "1", "2")

def test_undo_redo(calc):
    calc.evaluate("+", "1", "1")
    calc.undo()
    calc.redo()
    assert calc.caretaker.can_undo() or calc.caretaker.can_redo()

def test_clear_history(calc):
    calc.evaluate("+", "1", "1")
    assert not calc.history.df.empty
    calc.clear_history()
    assert calc.history.df.empty

def test_save_load(calc):
    calc.save("fake_path.csv")
    calc.load("fake_path.csv")  # no exceptions

def test_error_recorded_in_history(calc):
    with pytest.raises(CalculatorError):
        calc.evaluate("/", "1", "0")  # divide by zero
    last_entry = calc.history.df.iloc[-1]
    assert last_entry["result"] is None
    assert last_entry["error"] is not None

def test_auto_save_exception(calc):
    calc.config.CALCULATOR_AUTO_SAVE = True
    with patch.object(calc.history, "save", side_effect=Exception("fail")):
        # Should not raise outside CalculatorError
        result = calc.evaluate("+", "1", "2")
        assert result == 3

def test_parse_operands_failure(calc):
    # Invalid operands should raise CalculatorError
    with pytest.raises(CalculatorError):
        calc.evaluate("+", "bad", "input")

def test_repl_commands(monkeypatch):
    # Patch input and print to simulate user REPL input
    inputs = iter([
        "help",
        "history",
        "clear",
        "undo",
        "redo",
        "save",
        "load",
        "exit"
    ])
    outputs = []

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("builtins.print", lambda *a, **k: outputs.append(a))

    # Patch Calculator methods to avoid actual computation or file IO
    with patch("app.calculator_repl.Calculator.evaluate", return_value=42), \
         patch("app.calculator_repl.Calculator.undo"), \
         patch("app.calculator_repl.Calculator.redo"), \
         patch("app.calculator_repl.Calculator.save"), \
         patch("app.calculator_repl.Calculator.load"), \
         patch("app.calculator_repl.Calculator.clear_history"):
        repl()

    # Check that some key messages appeared
    help_msgs = [msg for msg in outputs if "Commands:" in msg[0]]
    assert help_msgs

def test_repl_operation(monkeypatch, calc):
    inputs = iter([
        "+",      # operation token
        "2",      # first number
        "3",      # second number
        "exit"
    ])
    outputs = []

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("builtins.print", lambda *a, **k: outputs.append(a))

    with patch("app.calculator_repl.Calculator.evaluate", return_value=5):
        repl()
        result_msgs = [msg for msg in outputs if "Result:" in msg[0]]
        assert any("Result: 5" in msg[0] for msg in result_msgs)

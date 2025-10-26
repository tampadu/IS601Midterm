import pytest
from pathlib import Path
from app.calculator_repl import Calculator, repl
from app.calculation import Calculation
from app.exceptions import CalculatorError


@pytest.fixture
def calc():
    return Calculator()


def test_evaluate_success(calc, monkeypatch):
    class FakeCalc:
        def __init__(self):
            self.operation_token = "+"
            self.a = 2.0
            self.b = 3.0
            self.error = None
            self.result = None

        def perform(self):
            self.result = self.a + self.b
            return self.result

    monkeypatch.setattr("app.calculation.CalculationFactory.create", lambda op, a, b: FakeCalc())

    result = calc.evaluate("+", "2", "3")
    assert result == 5
    assert calc.history.df.iloc[-1]["result"] == 5


def test_evaluate_failure(calc, monkeypatch):
    class FailCalc:
        def __init__(self):
            self.operation_token = "+"
            self.a = 2
            self.b = 0
            self.error = None
            self.result = None

        def perform(self):
            self.error = "fail"
            raise CalculatorError("fail")

    monkeypatch.setattr("app.calculation.CalculationFactory.create", lambda op, a, b: FailCalc())

    with pytest.raises(CalculatorError):
        calc.evaluate("+", "2", "0")

    assert calc.history.df.iloc[-1]["error"] == "fail"


def test_undo_redo(calc):
    # Simulate real usage so Caretaker has saved states
    calc.evaluate("+", "1", "2")  # triggers save internally
    calc.evaluate("-", "5", "2")  # triggers another save

    assert len(calc.history.df) == 2

    calc.undo()
    assert len(calc.history.df) == 1  # undo last change

    calc.redo()
    assert len(calc.history.df) == 2  # redo last change


def test_undo_empty_raises(calc):
    calc.caretaker._undos.clear()
    with pytest.raises(IndexError):
        calc.undo()


def test_redo_empty_raises(calc):
    calc.caretaker._redos.clear()
    with pytest.raises(IndexError):
        calc.redo()


def test_save_and_load(tmp_path, calc):
    path = tmp_path / "history.csv"
    calc.history.add("add", 1, 2, 3, None, "time")
    calc.save(str(path))
    assert path.exists()

    calc.clear_history()
    assert len(calc.history.df) == 0

    calc.load(str(path))
    assert len(calc.history.df) == 1


def test_clear_history(calc):
    calc.history.add("add", 1, 2, 3, None, "time")
    assert len(calc.history.df) == 1
    calc.clear_history()
    assert len(calc.history.df) == 0


@pytest.mark.parametrize("commands", [
    ["help", "exit"],
    ["history", "exit"],
    ["clear", "exit"],
    ["undo", "exit"],
    ["redo", "exit"],
    ["save", "exit"],
    ["load", "exit"],
])
def test_repl_commands(monkeypatch, commands):
    inputs = iter(commands)

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("builtins.print", lambda x: None)  # silence prints

    repl()


def test_repl_operation(monkeypatch):
    inputs = iter([
        "+",  # operation
        "2",  # first number
        "3",  # second number
        "exit"
    ])

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr("builtins.print", lambda x: None)

    repl()

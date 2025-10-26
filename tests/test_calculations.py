import pytest
from app.calculation import Calculation, CalculationFactory
from app.operations import Add
from app.exceptions import InvalidOperationError, OperandError


def test_calculation_perform_success(monkeypatch):
    calc = Calculation("add", 2, 3)

    # monkeypatch get_operation_instance to return Add instance
    monkeypatch.setattr("app.calculation.get_operation_instance", lambda token: Add())

    result = calc.perform()

    assert result == 5
    assert calc.result == 5
    assert calc.error is None


def test_calculation_perform_failure(monkeypatch):
    calc = Calculation("divide", 2, 0)

    # monkeypatch to use Divide
    from app.operations import Divide
    monkeypatch.setattr("app.calculation.get_operation_instance", lambda token: Divide())

    with pytest.raises(ZeroDivisionError):
        calc.perform()

    assert calc.result is None
    assert calc.error is not None


@pytest.mark.parametrize(
    "operation_token,a_raw,b_raw,expected_a,expected_b",
    [
        ("add", "2", "3", 2.0, 3.0),
        ("subtract", 5, 2, 5.0, 2.0),
        ("multiply", "4.5", "2", 4.5, 2.0),
    ]
)
def test_calculation_factory_create_success(operation_token, a_raw, b_raw, expected_a, expected_b):
    calc = CalculationFactory.create(operation_token, a_raw, b_raw)
    assert calc.a == expected_a
    assert calc.b == expected_b
    assert calc.operation_token == operation_token


@pytest.mark.parametrize(
    "operation_token,a_raw,b_raw,error_type",
    [
        ("", "1", "2", InvalidOperationError),  # empty token
        ("invalid", "1", "2", InvalidOperationError),  # invalid token
        ("add", "", "2", OperandError),  # empty first operand
        ("add", "1", "", OperandError),  # empty second operand
        ("add", "a", "2", OperandError),  # non-numeric first operand
        ("add", "1", "b", OperandError),  # non-numeric second operand
    ]
)
def test_calculation_factory_create_failure(operation_token, a_raw, b_raw, error_type):
    with pytest.raises(error_type):
        CalculationFactory.create(operation_token, a_raw, b_raw)

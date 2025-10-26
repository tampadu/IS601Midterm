import pytest
from app.exceptions import CalculatorError, InvalidOperationError, OperandError


# --- Basic Inheritance Tests ---

@pytest.mark.parametrize("exc_class", [InvalidOperationError, OperandError])
def test_exception_inherits_from_calculatorerror(exc_class):
    """Test that custom exceptions inherit from CalculatorError."""
    exc = exc_class("message")
    assert isinstance(exc, CalculatorError)
    assert str(exc) == "message"


def test_calculatorerror_is_base_exception():
    """Test CalculatorError inherits from Python's base Exception."""
    err = CalculatorError("base error")
    assert isinstance(err, Exception)
    assert str(err) == "base error"


# --- Raising Behavior ---

@pytest.mark.parametrize(
    "exc_class,message",
    [
        (InvalidOperationError, "Invalid operation"),
        (OperandError, "Bad operand"),
        (CalculatorError, "General calculator failure"),
    ],
)
def test_exceptions_raise_and_catch(exc_class, message):
    """Ensure all exceptions raise and can be caught properly."""
    with pytest.raises(exc_class, match=message):
        raise exc_class(message)

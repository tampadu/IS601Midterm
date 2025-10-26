# app/exceptions.py
class CalculatorError(Exception):
    """Base calculator exception."""


class InvalidOperationError(CalculatorError):
    """Raised when operation token is invalid."""


class OperandError(CalculatorError):
    """Raised when operands are invalid (non-numeric or empty)."""

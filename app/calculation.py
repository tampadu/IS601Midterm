# app/calculation.py
from dataclasses import dataclass
from typing import Any, Optional
from app.operations import get_operation_instance
from app.exceptions import InvalidOperationError, OperandError

@dataclass
class Calculation:
    operation_token: str
    a: float
    b: float
    result: Optional[float] = None
    error: Optional[str] = None

    def perform(self) -> float:
        op = get_operation_instance(self.operation_token)
        try:
            self.result = op.execute(self.a, self.b)
            return self.result
        except Exception as e:
            self.error = str(e)
            raise

class CalculationFactory:
    """Validates, converts, and returns a Calculation instance."""
    @staticmethod
    def create(operation_token: str, a_raw: Any, b_raw: Any) -> Calculation:
        if not operation_token or str(operation_token).strip() == "":
            raise InvalidOperationError("Operation must be provided")

        # Use LBYL small checks then EAFP conversion
        if isinstance(a_raw, str) and a_raw.strip() == "":
            raise OperandError("First operand empty")
        if isinstance(b_raw, str) and b_raw.strip() == "":
            raise OperandError("Second operand empty")

        try:
            a = float(a_raw)
            b = float(b_raw)
        except Exception as e:
            raise OperandError(f"Operands must be numbers: {e}")

        # verify operation exists (Factory)
        # get_operation_instance will raise InvalidOperationError if unknown
        _ = get_operation_instance(operation_token)

        return Calculation(operation_token, a, b)

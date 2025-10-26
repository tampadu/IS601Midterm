from __future__ import annotations
from typing import Protocol, Dict, Callable
from app.exceptions import InvalidOperationError

class OperationStrategy(Protocol):
    def execute(self, a: float, b: float) -> float:
        ...

class Add:
    name = "add"
    symbol = "+"

    def execute(self, a: float, b: float) -> float:
        return a + b

class Subtract:
    name = "subtract"
    symbol = "-"

    def execute(self, a: float, b: float) -> float:
        return a - b

class Multiply:
    name = "multiply"
    symbol = "*"

    def execute(self, a: float, b: float) -> float:
        return a * b

class Divide:
    name = "divide"
    symbol = "/"

    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return a / b

class Power:
    name = "power"
    symbol = "**"

    def execute(self, a: float, b: float) -> float:
        return a ** b

class Root:
    name = "root"
    symbol = "root"

    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Root degree cannot be zero")
        # handle negative a with integer odd roots
        if a < 0:
            if int(b) % 2 == 0:
                raise ValueError("Even root of negative number not supported")
            return -((-a) ** (1.0 / b))
        return a ** (1.0 / b)

class Modulus:
    name = "modulus"
    symbol = "%"

    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("Cannot modulus by zero")
        return a % b

class IntDivide:
    name = "int_divide"
    symbol = "//"

    def execute(self, a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("Cannot integer-divide by zero")
        return a // b

class Percent:
    name = "percent"
    symbol = "percent"

    def execute(self, a: float, b: float) -> float:
        # Percentage(a, b) => (a / b) * 100
        if b == 0:
            raise ZeroDivisionError("Cannot compute percentage with denominator zero")
        return (a / b) * 100.0

class AbsDiff:
    name = "abs_diff"
    symbol = "abs"

    def execute(self, a: float, b: float) -> float:
        return abs(a - b)

# registry
_OPERATION_REGISTRY: Dict[str, Callable[[], OperationStrategy]] = {
    Add.name: Add, Add.symbol: Add,
    Subtract.name: Subtract, Subtract.symbol: Subtract,
    Multiply.name: Multiply, Multiply.symbol: Multiply,
    Divide.name: Divide, Divide.symbol: Divide,
    Power.name: Power, Power.symbol: Power,
    Root.name: Root, Root.symbol: Root,
    Modulus.name: Modulus, Modulus.symbol: Modulus,
    IntDivide.name: IntDivide, IntDivide.symbol: IntDivide,
    Percent.name: Percent, Percent.symbol: Percent,
    AbsDiff.name: AbsDiff, AbsDiff.symbol: AbsDiff,
}

def get_operation_instance(token: str) -> OperationStrategy:
    t = str(token).strip().lower()
    cls = _OPERATION_REGISTRY.get(t)
    if not cls:
        raise InvalidOperationError(f"Invalid operation: {token}")
    return cls()

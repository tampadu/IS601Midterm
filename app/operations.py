# app/operations.py
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
        if a < 0:
            if int(b) % 2 == 0:
                raise ValueError("Even root of negative number not supported")
            return -((-a) ** (1.0 / b))  # handle odd root of negative
        return a ** (1.0 / b)


# registry
_OPERATION_REGISTRY: Dict[str, Callable[[], OperationStrategy]] = {
    Add.name: Add, Add.symbol: Add,
    Subtract.name: Subtract, Subtract.symbol: Subtract,
    Multiply.name: Multiply, Multiply.symbol: Multiply,
    Divide.name: Divide, Divide.symbol: Divide,
    Power.name: Power, Power.symbol: Power,
    Root.name: Root, Root.symbol: Root
}

def get_operation_instance(token: str) -> OperationStrategy:
    t = str(token).strip().lower()
    cls = _OPERATION_REGISTRY.get(t)
    if not cls:
        raise InvalidOperationError(f"Invalid operation: {token}")
    return cls()

# app/input_validators.py
from typing import Tuple
from app.exceptions import OperandError

def parse_operands_lbyl(a_raw: str, b_raw: str) -> Tuple[float, float]:
    if a_raw is None or a_raw.strip() == "":
        raise OperandError("First operand empty")
    if b_raw is None or b_raw.strip() == "":
        raise OperandError("Second operand empty")
    try:
        return float(a_raw), float(b_raw)
    except ValueError as e:
        raise OperandError(f"Operands must be numeric: {e}")

def parse_operands_eafp(a_raw: str, b_raw: str) -> Tuple[float, float]:
    try:
        return float(a_raw), float(b_raw)
    except Exception as e:
        raise OperandError(f"Operands must be numeric: {e}")

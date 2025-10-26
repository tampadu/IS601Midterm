import pytest
from app.input_validators import parse_operands_lbyl, parse_operands_eafp
from app.exceptions import OperandError

@pytest.mark.parametrize(
    "a_raw,b_raw,expected",
    [
        ("3", "4", (3.0, 4.0)),
        ("3.5", "2.5", (3.5, 2.5)),
        ("  7  ", "  8  ", (7.0, 8.0)),
        ("0", "0", (0.0, 0.0)),
        ("-5", "10", (-5.0, 10.0)),
    ],
)
def test_parse_operands_lbyl_valid(a_raw, b_raw, expected):
    """Valid inputs should return correct float tuples."""
    assert parse_operands_lbyl(a_raw, b_raw) == expected


@pytest.mark.parametrize(
    "a_raw,b_raw,expected_msg",
    [
        (None, "2", "First operand empty"),
        ("", "2", "First operand empty"),
        (" ", "3", "First operand empty"),
        ("3", None, "Second operand empty"),
        ("3", "", "Second operand empty"),
        ("3", " ", "Second operand empty"),
    ],
)
def test_parse_operands_lbyl_empty_operands(a_raw, b_raw, expected_msg):
    """Empty or None operands should raise OperandError."""
    with pytest.raises(OperandError, match=expected_msg):
        parse_operands_lbyl(a_raw, b_raw)


@pytest.mark.parametrize(
    "a_raw,b_raw",
    [
        ("abc", "3"),
        ("3", "xyz"),
        ("3.2.1", "2"),
        ("1", "2,5"),
    ],
)
def test_parse_operands_lbyl_non_numeric(a_raw, b_raw):
    """Non-numeric inputs should raise OperandError."""
    with pytest.raises(OperandError, match="Operands must be numeric"):
        parse_operands_lbyl(a_raw, b_raw)


# ---- Tests for EAFP version ----

@pytest.mark.parametrize(
    "a_raw,b_raw,expected",
    [
        ("5", "6", (5.0, 6.0)),
        ("0", "-1", (0.0, -1.0)),
        ("3.14", "2.71", (3.14, 2.71)),
    ],
)
def test_parse_operands_eafp_valid(a_raw, b_raw, expected):
    """EAFP valid numeric conversion."""
    assert parse_operands_eafp(a_raw, b_raw) == expected


@pytest.mark.parametrize(
    "a_raw,b_raw",
    [
        ("abc", "3"),
        ("", "2"),
        (None, "1"),
        ("1", None),
        ("3.5", "two"),
    ],
)
def test_parse_operands_eafp_invalid(a_raw, b_raw):
    """EAFP invalid conversion should raise OperandError."""
    with pytest.raises(OperandError, match="Operands must be numeric"):
        parse_operands_eafp(a_raw, b_raw)

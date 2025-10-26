import pytest
from app.operations import (
    Add, Subtract, Multiply, Divide, Power, Root,
    get_operation_instance, _OPERATION_REGISTRY
)
from app.exceptions import InvalidOperationError


@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (-1, 5, 4),
    (0, 0, 0),
])
def test_add_execute(a, b, expected):
    assert Add().execute(a, b) == expected


@pytest.mark.parametrize("a,b,expected", [
    (5, 3, 2),
    (-1, -1, 0),
    (0, 10, -10),
])
def test_subtract_execute(a, b, expected):
    assert Subtract().execute(a, b) == expected


@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 6),
    (0, 5, 0),
    (-2, 3, -6),
])
def test_multiply_execute(a, b, expected):
    assert Multiply().execute(a, b) == expected


def test_divide_execute_normal_cases():
    assert Divide().execute(6, 3) == 2
    assert pytest.approx(Divide().execute(5, 2)) == 2.5


def test_divide_by_zero_raises():
    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
        Divide().execute(1, 0)


@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 8),
    (5, 0, 1),
    (4, 0.5, 2),
])
def test_power_execute(a, b, expected):
    assert pytest.approx(Power().execute(a, b)) == expected


@pytest.mark.parametrize("a,b,expected", [
    (27, 3, 3),       # cube root
    (16, 2, 4),       # square root
    (1, 5, 1),
])
def test_root_execute_valid(a, b, expected):
    assert pytest.approx(Root().execute(a, b)) == expected


def test_root_degree_zero_raises():
    with pytest.raises(ValueError, match="Root degree cannot be zero"):
        Root().execute(8, 0)


def test_root_even_root_of_negative_raises():
    with pytest.raises(ValueError, match="Even root of negative number"):
        Root().execute(-16, 2)


def test_root_odd_root_of_negative_ok():
    # cube root of -8 should be -2
    assert pytest.approx(Root().execute(-8, 3)) == -2


@pytest.mark.parametrize("token,cls", [
    ("add", Add),
    ("+", Add),
    ("subtract", Subtract),
    ("-", Subtract),
    ("multiply", Multiply),
    ("*", Multiply),
    ("divide", Divide),
    ("/", Divide),
    ("power", Power),
    ("**", Power),
    ("root", Root),
])
def test_get_operation_instance_valid(token, cls):
    op = get_operation_instance(token)
    assert isinstance(op, cls)
    assert hasattr(op, "execute")
    assert callable(op.execute)


@pytest.mark.parametrize("token", ["invalid", "", "   ", "foo"])
def test_get_operation_instance_invalid(token):
    with pytest.raises(InvalidOperationError, match="Invalid operation"):
        get_operation_instance(token)


def test_registry_contains_expected_keys():
    """Ensure registry includes all operations and symbols."""
    expected_tokens = {
        "add", "+", "subtract", "-", "multiply", "*",
        "divide", "/", "power", "**", "root", "root"
    }
    assert expected_tokens.issubset(set(_OPERATION_REGISTRY.keys()))

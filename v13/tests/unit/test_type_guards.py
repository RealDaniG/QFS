import pytest
from enum import Enum
from v13.libs.BigNum128 import BigNum128
from v13.libs.type_guards import ensure_bignum, ensure_int, safe_enum_serialize


class TestEnum(Enum):
    TEST_A = "value_a"
    TEST_B = "value_b"


def test_ensure_bignum():
    # BigNum -> BigNum
    bn = BigNum128.from_int(100)
    assert ensure_bignum(bn) == bn

    # int -> BigNum
    assert ensure_bignum(100).value == bn.value

    # str -> BigNum
    assert ensure_bignum("100").value == bn.value

    # Invalid
    with pytest.raises(TypeError):
        ensure_bignum(10.5)


def test_ensure_int():
    # int -> int
    assert ensure_int(100) == 100

    # BigNum -> int
    bn = BigNum128.from_int(200)
    assert ensure_int(bn) == 200 * BigNum128.SCALE  # SCALE handled in wrapper

    # Note: ensure_int returns .value (atomic units) for BigNum
    # So 200 * 10^16 is expected

    # Invalid
    with pytest.raises(TypeError):
        ensure_int("100")


def test_safe_enum_serialize():
    # Enum -> str
    assert safe_enum_serialize(TestEnum.TEST_A) == "value_a"

    # str -> str
    assert safe_enum_serialize("value_a") == "value_a"

    # Object with value attr
    class MockEnum:
        value = "mock_value"

    assert safe_enum_serialize(MockEnum()) == "mock_value"

    # Invalid
    with pytest.raises(TypeError):
        safe_enum_serialize(123)

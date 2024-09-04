from algopy import Bytes, BigUInt
from puya_bignumber.bignumber import (
    add_bytes,
    subtract_bytes,
    big_endian_equal,
    multiply,
    divide,
)
import os
import random


def assert_mul(a_bytes: bytes, b_bytes: bytes):
    a_int = int.from_bytes(a_bytes)
    b_int = int.from_bytes(b_bytes)

    ab_int = a_int * b_int
    ab_bytes = ab_int.to_bytes((ab_int.bit_length() + 8) // 8)

    result: Bytes = multiply(Bytes(a_bytes), Bytes(b_bytes))
    assert big_endian_equal(
        Bytes(ab_bytes), result
    ), f"Multiply: Must be equal. {a_int}x{b_int}={ab_int}. Got {result}."


def assert_add(a_bytes: bytes, b_bytes: bytes):
    a_int = int.from_bytes(a_bytes)
    b_int = int.from_bytes(b_bytes)

    ab_int = a_int + b_int
    ab_bytes = ab_int.to_bytes((ab_int.bit_length() + 8) // 8)

    result: Bytes = add_bytes(Bytes(a_bytes), Bytes(b_bytes))
    assert big_endian_equal(
        Bytes(ab_bytes), result
    ), f"Add: Must be equal. {a_int}+{b_int}={ab_int}. Got {result}."


def assert_subtract(a_bytes: bytes, b_bytes: bytes):
    a_int = int.from_bytes(a_bytes, byteorder="big")
    b_int = int.from_bytes(b_bytes, byteorder="big")
    if a_int < b_int:
        tmp = a_int
        a_int = b_int
        b_int = tmp

    a_bytes = a_int.to_bytes((a_int.bit_length() + 8) // 8)
    b_bytes = b_int.to_bytes((b_int.bit_length() + 8) // 8)

    ab_int = a_int - b_int

    result: Bytes = subtract_bytes(Bytes(a_bytes), Bytes(b_bytes))
    assert big_endian_equal(
        Bytes(ab_int.to_bytes(1 + (ab_int.bit_length() + 8) // 8)), result
    ), f"Subtract: Must be equal. {a_int}-{b_int}={ab_int}. Got {result}."


def assert_divide(a_bytes: bytes, b_bytes: bytes):
    a_int = int.from_bytes(a_bytes, byteorder="big")
    b_int = max(int.from_bytes(b_bytes, byteorder="big"), 1)

    a_bytes = a_int.to_bytes((a_int.bit_length() + 8) // 8)
    b_bytes = b_int.to_bytes((b_int.bit_length() + 8) // 8)

    assert b_int > 0, f"Divisor must be at least 1. a={a_int}, b={b_int}"
    base = 2**256
    result: Bytes = divide(Bytes(a_bytes), Bytes(b_bytes), BigUInt(base))
    expected: int = a_int // b_int
    byte_length: int = (expected.bit_length() + 8) // 8
    expected_bytes: bytes = expected.to_bytes(byte_length, "big")

    assert big_endian_equal(
        result, Bytes(expected_bytes)
    ), f"Divide: Must be equal. {a_int}//{b_int}={expected}. Got {result}."


def test_all():
    assert_add(int(2**32 - 1).to_bytes(4), int(0).to_bytes(4))
    assert_add(int(0).to_bytes(4), int(0).to_bytes(4))
    assert_subtract(int(2**32 - 1).to_bytes(4), int(2**32 - 1).to_bytes(4))
    assert_subtract(int(2**32 - 1).to_bytes(4), int(0).to_bytes(4))
    assert_subtract(int(0).to_bytes(4), int(0).to_bytes(4))

    for _ in range(10_000):
        a_bytes = os.urandom(random.randint(1, 1024))
        b_bytes = os.urandom(random.randint(1, 1024))
        assert_divide(a_bytes, b_bytes)
        assert_mul(a_bytes, b_bytes)
        assert_add(a_bytes, b_bytes)
        assert_subtract(a_bytes, b_bytes)

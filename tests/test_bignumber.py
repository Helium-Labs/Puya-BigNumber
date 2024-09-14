from algopy import Bytes
from puya_bignumber import (
    add,
    subtract,
    equal,
    multiply,
    divide,
    less_than,
    greater_than,
    mod_barrett_reduce,
    barrett_reducer_factor,
    modexp_barrett_reduce,
)
from .build import build
import os
import random
import base64


def get_barrett_precomputed_factor(mod: bytes) -> bytes:
    mod_int: int = int.from_bytes(mod)
    shift: int = len(mod) * 2 * 8
    factor: int = 2**shift // mod_int
    factor_bytes: bytes = factor.to_bytes((factor.bit_length() + 7) // 8)
    return factor_bytes


def assert_equal(a_bytes: bytes, b_bytes: bytes):
    a_int = int.from_bytes(a_bytes)
    b_int = int.from_bytes(b_bytes)
    ab_int = a_int == b_int
    result = equal(Bytes(a_bytes), Bytes(b_bytes))
    assert (
        result == ab_int
    ), f"Equal: Must be equal. {a_int}=={b_int}={ab_int}. Got {result}."
    assert equal(
        Bytes(a_bytes), Bytes(a_bytes)
    ), f"Equal: Must be equal. {a_int}=={b_int}={ab_int}. Got {False}."


def assert_less_than(a_bytes: bytes, b_bytes: bytes):
    a_int = int.from_bytes(a_bytes)
    b_int = int.from_bytes(b_bytes)
    ab_int = a_int < b_int
    result: bool = less_than(Bytes(a_bytes), Bytes(b_bytes))
    assert (
        ab_int == result
    ), f"Less Than: Must be equal. {a_int}<{b_int}={ab_int}. Got {result}."


def assert_modexp_barrett_reduce(base: bytes, exp: bytes, mod: bytes):
    base_int: int = int.from_bytes(base)
    exp_int: int = int.from_bytes(exp)
    mod_int: int = int.from_bytes(mod)
    expected_int: int = pow(base_int, exp_int, mod_int)
    ab_bytes = expected_int.to_bytes((expected_int.bit_length() + 7) // 8)
    factor_bytes: bytes = get_barrett_precomputed_factor(mod)
    result = modexp_barrett_reduce(
        Bytes(base), Bytes(exp), Bytes(mod), Bytes(factor_bytes)
    )
    assert equal(
        Bytes(ab_bytes), result
    ), f"Modulo with Barrett Reduction: Must be equal. ({base_int}^{exp_int})%{mod_int}={expected_int}. Got {result}."


def assert_mod_barrett_reduce(a_bytes: bytes, mod: bytes):
    a_int: int = int.from_bytes(a_bytes)
    b_int: int = int.from_bytes(mod)
    ab_int: int = a_int % b_int
    ab_bytes = ab_int.to_bytes((ab_int.bit_length() + 7) // 8)
    factor_bytes: bytes = get_barrett_precomputed_factor(mod)
    result = mod_barrett_reduce(Bytes(a_bytes), Bytes(mod), Bytes(factor_bytes))
    assert equal(
        Bytes(ab_bytes), result
    ), f"Modulo with Barrett Reduction: Must be equal. {a_int}%{b_int}={ab_int}. Got {result}."


def assert_barrett_reducer_factor(mod: bytes):
    factor: bytes = get_barrett_precomputed_factor(mod)
    result = barrett_reducer_factor(Bytes(mod))
    assert equal(
        Bytes(factor), result
    ), f"Barrett Reducter Factor: Must be equal. Factor={factor}. Got {result}."


def assert_greater_than(a_bytes: bytes, b_bytes: bytes):
    a_int = int.from_bytes(a_bytes)
    b_int = int.from_bytes(b_bytes)
    ab_int = a_int > b_int
    result: bool = greater_than(Bytes(a_bytes), Bytes(b_bytes))
    assert (
        ab_int == result
    ), f"Greater Than: Must be equal. {a_int}>{b_int}={ab_int}. Got {result}."


def assert_mul(a_bytes: bytes, b_bytes: bytes):
    a_int = int.from_bytes(a_bytes)
    b_int = int.from_bytes(b_bytes)

    ab_int = a_int * b_int
    ab_bytes = ab_int.to_bytes((ab_int.bit_length() + 7) // 8)

    result: Bytes = multiply(Bytes(a_bytes), Bytes(b_bytes))
    assert equal(
        Bytes(ab_bytes), result
    ), f"Multiply: Must be equal. {a_int}x{b_int}={ab_int}. Got {result}."


def assert_add(a_bytes: bytes, b_bytes: bytes):
    a_int = int.from_bytes(a_bytes)
    b_int = int.from_bytes(b_bytes)

    ab_int = a_int + b_int
    ab_bytes = ab_int.to_bytes((ab_int.bit_length() + 7) // 8)

    result: Bytes = add(Bytes(a_bytes), Bytes(b_bytes))
    assert equal(
        Bytes(ab_bytes), result
    ), f"Add: Must be equal. {a_int}+{b_int}={ab_int}. Got {result}."


def assert_subtract(a_bytes: bytes, b_bytes: bytes):
    a_int = int.from_bytes(a_bytes, byteorder="big")
    b_int = int.from_bytes(b_bytes, byteorder="big")
    if a_int < b_int:
        tmp = a_int
        a_int = b_int
        b_int = tmp

    a_bytes = a_int.to_bytes((a_int.bit_length() + 7) // 8)
    b_bytes = b_int.to_bytes((b_int.bit_length() + 7) // 8)

    ab_int = a_int - b_int

    result: Bytes = subtract(Bytes(a_bytes), Bytes(b_bytes))
    assert equal(
        Bytes(ab_int.to_bytes(1 + (ab_int.bit_length() + 7) // 8)), result
    ), f"Subtract: Must be equal. {a_int}-{b_int}={ab_int}. Got {result}."


def assert_divide(a_bytes: bytes, b_bytes: bytes):
    a_int = int.from_bytes(a_bytes, byteorder="big")
    b_int = max(int.from_bytes(b_bytes, byteorder="big"), 1)

    result: Bytes = divide(Bytes(a_bytes), Bytes(b_bytes))
    expected: int = a_int // b_int
    byte_length: int = (expected.bit_length() + 7) // 8
    expected_bytes: bytes = expected.to_bytes(byte_length, "big")

    assert equal(
        result, Bytes(expected_bytes)
    ), f"Divide: Must be equal. {a_int}//{b_int}={expected}. Got {result}."


def test_all():
    # Test that it compiles
    build("./tests", "tester_contract")
    # Test that operators are accurate
    EXTREME_DIVIDEND = int(2**3600).to_bytes(451)
    EXTREME_DIVISOR_B64 = "/6fyvwqQ+ln4tmR0bFiDFnVMEHQkJcpMWOm+eR/EfQwp9b2glCuQ8wYLjcK0CfNTq2rWGv69XugNhXIrMKX8W9Fh4rh1RrrNRsrg1oj2+ppDiyRe+TL3UexbwCYlT3Is0i6iz4+ZTQVdru8pjHqtxKrtmnREB4kRszANhVJ8N4uBXxCMA/z5zLRo+/B8EZUuBSdTJUlz62E6edyNykGIqPPEzzxJZKZL0yOG3TJu5Pch0Y9nzwXJs8PcUGCG22wcCwakXXUT7D3cQ3WpztcRBXBtxfivmmqvT8ixSnLuws0h"
    assert_divide(EXTREME_DIVIDEND, base64.b64decode(EXTREME_DIVISOR_B64))

    assert_add(int(2**32 - 1).to_bytes(4), int(0).to_bytes(4))
    assert_add(int(0).to_bytes(4), int(0).to_bytes(4))
    assert_subtract(int(2**32 - 1).to_bytes(4), int(2**32 - 1).to_bytes(4))
    assert_subtract(int(2**32 - 1).to_bytes(4), int(0).to_bytes(4))
    assert_subtract(int(0).to_bytes(4), int(0).to_bytes(4))
    assert_less_than(int(2**32 - 1).to_bytes(4), int(0).to_bytes(4))
    assert_less_than(int(0).to_bytes(4), int(2**32 - 1).to_bytes(4))
    assert_greater_than(int(2**32 - 1).to_bytes(4), int(0).to_bytes(4))
    assert_greater_than(int(0).to_bytes(4), int(2**32 - 1).to_bytes(4))

    NUM_TESTS = 30_000
    for _ in range(NUM_TESTS):
        MAX_WIDTH = 1024
        a_bytes = os.urandom(random.randint(2, MAX_WIDTH))
        b_bytes = os.urandom(random.randint(2, MAX_WIDTH))
        assert_equal(a_bytes, b_bytes)
        assert_less_than(a_bytes, b_bytes)
        assert_greater_than(a_bytes, b_bytes)
        assert_divide(a_bytes, b_bytes)
        assert_mul(a_bytes, b_bytes)
        assert_add(a_bytes, b_bytes)
        assert_subtract(a_bytes, b_bytes)

    for _ in range(NUM_TESTS):
        # Generate a random modulus that is not a power of 2
        MAX_WIDTH = 1024
        mod_bytes = os.urandom(random.randint(1, MAX_WIDTH))
        mod = int.from_bytes(mod_bytes)
        while mod & (mod - 1) == 0:
            mod_bytes = os.urandom(random.randint(1, MAX_WIDTH))

        # Generate a random x in the range [0, mod^2)
        a = random.randint(0, mod**2 - 1)
        a_bytes = a.to_bytes((a.bit_length() + 7) // 8)
        assert_barrett_reducer_factor(mod_bytes)
        assert_mod_barrett_reduce(a_bytes, mod_bytes)
        MAX_EXP_WIDTH = 64
        exp_bytes = os.urandom(random.randint(2, MAX_EXP_WIDTH))
        assert_modexp_barrett_reduce(a_bytes, exp_bytes, mod_bytes)

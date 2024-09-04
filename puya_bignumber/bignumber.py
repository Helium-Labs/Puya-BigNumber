from algopy import arc4, Bytes, subroutine, BigUInt, UInt64, urange
from algopy.op import substring, bzero, concat, extract, itob, btoi
from .common import (
    pad,
    max_value,
    enclosing_multiple,
    pad_as_multiple,
    decode_dynamic_bytes,
)
import typing

BIGINT_BYTE_SIZE: UInt64 = UInt64(64)
UINT256_BYTE_SIZE: UInt64 = UInt64(32)
UInt256: typing.TypeAlias = arc4.BigUIntN[typing.Literal[256]]


@subroutine
def add(a_in: Bytes, b_in: Bytes) -> Bytes:

    length: UInt64 = enclosing_multiple(
        max_value(a_in.length, b_in.length), BIGINT_BYTE_SIZE
    )
    a: Bytes = pad(a_in, length)
    b: Bytes = pad(b_in, length)

    assert a.length % BIGINT_BYTE_SIZE == 0, "a length must be multiple of width"
    assert b.length % BIGINT_BYTE_SIZE == 0, "b length must be multiple of width"

    n: UInt64 = a.length // BIGINT_BYTE_SIZE
    result: Bytes = Bytes(b"")
    carry: UInt64 = UInt64(0)
    for i in reversed(urange(n)):
        a_slice: BigUInt = BigUInt.from_bytes(
            extract(a, i * BIGINT_BYTE_SIZE, BIGINT_BYTE_SIZE)
        )
        b_slice: BigUInt = BigUInt.from_bytes(
            extract(b, i * BIGINT_BYTE_SIZE, BIGINT_BYTE_SIZE)
        )

        sum: BigUInt = a_slice + b_slice
        sum_bytes: Bytes = pad(sum.bytes, BIGINT_BYTE_SIZE + 1)
        sum_carry = btoi(sum_bytes[0])

        ab_carry: BigUInt = BigUInt.from_bytes(sum_bytes[1:]) + carry
        ab_carry_bytes: Bytes = pad(ab_carry.bytes, BIGINT_BYTE_SIZE + 1)
        ab_carry_carry = btoi(ab_carry_bytes[0])

        result = concat(ab_carry_bytes[1:], result)
        carry = ab_carry_carry + sum_carry

    if carry == 0:
        return result

    carry_bytes: Bytes = itob(carry)[7]
    return concat(carry_bytes, result)


@subroutine
def subtract(a_in: Bytes, b_in: Bytes) -> Bytes:
    # Assume a_in >= b_in
    # 0 - 0 case
    if a_in.length == 0 or a_in == bzero(b_in.length):
        return a_in
    # a - 0 case
    if b_in.length == 0 or b_in == bzero(b_in.length):
        return a_in
    length: UInt64 = enclosing_multiple(
        max_value(a_in.length, b_in.length), BIGINT_BYTE_SIZE
    )
    a: Bytes = pad(a_in, length)
    b: Bytes = pad(b_in, length)
    if a == b:
        return bzero(a.length)
    ones_complement: Bytes = ~b
    twos_complement: Bytes = add(ones_complement, itob(1))
    a_inv_b: Bytes = add(a, twos_complement)
    return a_inv_b[1:]


@subroutine
def big_endian_equal(a: Bytes, b: Bytes) -> bool:
    length: UInt64 = max_value(a.length, b.length)
    padded_a = pad(a, length)
    padded_b = pad(b, length)
    are_equal: bool = padded_a == padded_b
    return are_equal


# Karatsuba algorithm by Anatoly Karatsuba
@subroutine
def multiply(X: Bytes, Y: Bytes) -> Bytes:
    length: UInt64 = enclosing_multiple(max_value(X.length, Y.length), BIGINT_BYTE_SIZE)
    X: Bytes = pad(X, length)
    Y: Bytes = pad(Y, length)

    N: UInt64 = X.length
    if N <= BIGINT_BYTE_SIZE:
        XB: BigUInt = BigUInt.from_bytes(X)
        YB: BigUInt = BigUInt.from_bytes(Y)
        XYB: BigUInt = XB * YB
        return XYB.bytes

    fh: UInt64 = N // 2
    sh: UInt64 = N - fh

    xL: Bytes = X[:fh]
    xR: Bytes = X[fh:]
    yL: Bytes = Y[:fh]
    yR: Bytes = Y[fh:]

    P1: Bytes = multiply(xL, yL)
    P2: Bytes = multiply(xR, yR)
    P3: Bytes = multiply(add(xL, xR), add(yL, yR))
    P4: Bytes = subtract(subtract(P3, P1), P2)
    shifted_P1: Bytes = concat(P1, bzero(2 * sh))
    shifted_P4: Bytes = concat(P4, bzero(sh))
    return add(add(shifted_P1, shifted_P4), P2)


@subroutine
def bytes_to_BE_digits(num: Bytes) -> arc4.DynamicArray[UInt256]:
    digits: arc4.DynamicArray[UInt256] = arc4.DynamicArray[UInt256]()
    zero: UInt256 = UInt256.from_bytes(bzero(UINT256_BYTE_SIZE))
    digits.append(zero)
    padded: Bytes = pad_as_multiple(num, UINT256_BYTE_SIZE)
    num_digits: UInt64 = padded.length // UINT256_BYTE_SIZE
    for i in urange(num_digits):
        digit_bytes: Bytes = extract(padded, i * UINT256_BYTE_SIZE, UINT256_BYTE_SIZE)
        digit: UInt256 = UInt256.from_bytes(digit_bytes)
        digits.append(digit)
    return digits


@subroutine
def BE_digits_to_bytes(digits: arc4.DynamicArray[UInt256]) -> Bytes:
    return decode_dynamic_bytes(digits.bytes)


@subroutine
def biguint_to_digit(num: BigUInt) -> UInt256:
    if num.bytes.length == 0:
        return UInt256.from_bytes(bzero(UINT256_BYTE_SIZE))

    padded: Bytes = pad_as_multiple(num.bytes, UINT256_BYTE_SIZE)
    exact_bytes: Bytes = substring(
        padded, padded.length - UINT256_BYTE_SIZE, padded.length
    )
    digit: UInt256 = UInt256.from_bytes(exact_bytes)
    return digit


@subroutine
def _multiply_word(
    digits: arc4.DynamicArray[UInt256], n: UInt64, d: UInt64, base: BigUInt
) -> arc4.DynamicArray[UInt256]:
    c: BigUInt = BigUInt(0)
    for i in reversed(urange(1, n + 1)):
        digit: BigUInt = BigUInt.from_bytes(digits[i].bytes)
        p: BigUInt = d * digit + c
        pModBase: BigUInt = p % base
        normalized_digit: UInt256 = biguint_to_digit(pModBase)
        digits[i] = normalized_digit
        c = p // base
    digits[0] = biguint_to_digit(c)
    return digits


@subroutine
def _divide_word(
    u_raw: arc4.DynamicArray[UInt256], v_digit: BigUInt, base: BigUInt
) -> Bytes:
    r: BigUInt = BigUInt(0)
    for i in urange(u_raw.length):
        digit: BigUInt = BigUInt.from_bytes(u_raw[i].bytes)
        p: BigUInt = digit + r * base
        q_digit: BigUInt = p // v_digit
        u_raw[i] = biguint_to_digit(q_digit)
        r = p - q_digit * v_digit
    q: Bytes = BE_digits_to_bytes(u_raw)
    return q


# Algorithm D by Robert Knuth
@subroutine
def divide(u_num: Bytes, v_num: Bytes, base: BigUInt) -> Bytes:
    assert u_num.length >= 1, f"u_num must have at least one byte {u_num}"
    assert v_num.length >= 1, "v_num must have at least one byte"

    u_raw: arc4.DynamicArray[UInt256] = bytes_to_BE_digits(u_num)
    v_raw: arc4.DynamicArray[UInt256] = bytes_to_BE_digits(v_num)
    assert v_raw[-1] != 0, "Non-zero divisor"

    n: UInt64 = v_raw.length - 1
    if u_raw.length < v_raw.length:
        # The divisor is larger than the dividend
        return itob(0)
    if u_raw[-1] == 0:
        # The dividend is 0
        return itob(0)

    assert n >= 1, "At least 1 digit divisor"

    m: UInt64 = u_raw.length - v_raw.length
    q: arc4.DynamicArray[UInt256] = arc4.DynamicArray[UInt256]()

    v_raw_1: BigUInt = BigUInt.from_bytes(v_raw[1].bytes)
    if n == 1:
        return _divide_word(u_raw, v_raw_1, base)

    # Step D2: Normalize
    norm: BigUInt = base // (v_raw_1 + 1)
    u: arc4.DynamicArray[UInt256] = _multiply_word(u_raw, m + n, norm, base)
    v: arc4.DynamicArray[UInt256] = _multiply_word(v_raw, n, norm, base)
    v_1: BigUInt = BigUInt.from_bytes(v[1].bytes)
    # Step D3: Loop on j
    v_2: BigUInt = BigUInt.from_bytes(v[2].bytes)
    for j in urange(m + 1):
        # Step D3: Calculate estimated q
        u_j: BigUInt = BigUInt.from_bytes(u[j].bytes)
        u_j1: BigUInt = BigUInt.from_bytes(u[j + 1].bytes)

        qpart: BigUInt = base * u_j + u_j1
        qhat: BigUInt = qpart // v_1
        if u_j >= v_1:
            qhat = base - 1

        # Correct quotient estimate if too large
        u_j2: BigUInt = BigUInt.from_bytes(u[j + 2].bytes)
        qhat_test: BigUInt = qhat * v_1 + ((qhat * v_2) // base)
        qhat_cond: BigUInt = qpart + (u_j2 // base)
        while qhat_test > qhat_cond:
            qhat -= 1
            qhat_test = qhat * v_1 + ((qhat * v_2) // base)

        # Step D4: Multiply and subtract
        c: BigUInt = BigUInt(0)
        c_is_neg: bool = False
        for i in reversed(urange(1, n + 1)):
            u_ji: BigUInt = BigUInt.from_bytes(u[j + i].bytes)
            v_i: BigUInt = BigUInt.from_bytes(v[i].bytes)
            assert c >= 0, "C must be Positive"
            if c_is_neg:
                # Handle case when c is considered negative
                if u_ji >= qhat * v_i + c:
                    # Positive outcome
                    p: BigUInt = u_ji - (qhat * v_i + c)
                    assert p >= 0, "P must be Positive"
                    pModBase: BigUInt = p % base
                    u[j + i] = biguint_to_digit(pModBase)
                    c = p // base
                    c_is_neg = False
                else:
                    # Negative outcome
                    p: BigUInt = (qhat * v_i + c) - u_ji
                    assert p >= 0, "P must be Positive"
                    pModBase: BigUInt = base - (p % base)
                    u[j + i] = biguint_to_digit(pModBase)
                    c = (p // base) + 1  # Adjust for base correction
                    c_is_neg = True
            else:
                # Handle case when c is considered positive
                if u_ji + c >= qhat * v_i:
                    # Positive outcome
                    p: BigUInt = (u_ji + c) - qhat * v_i
                    assert p >= 0, "P must be Positive"
                    pModBase: BigUInt = p % base
                    u[j + i] = biguint_to_digit(pModBase)
                    c = p // base
                    c_is_neg = False
                else:
                    # Negative outcome
                    p: BigUInt = (qhat * v_i) - (u_ji + c)
                    assert p >= 0, "P must be Positive"
                    pModBase: BigUInt = base - (p % base)
                    u[j + i] = biguint_to_digit(pModBase)
                    c = (p // base) + 1  # Adjust for base correction
                    c_is_neg = True

        # Step D5: Test remainder
        if c > u_j and c_is_neg and (c - u_j) >= base:
            # Step D6: Add back
            qhat -= 1

        qhat_digit = biguint_to_digit(qhat)
        q.append(qhat_digit)

    q_as_bytes: Bytes = BE_digits_to_bytes(q)

    return q_as_bytes

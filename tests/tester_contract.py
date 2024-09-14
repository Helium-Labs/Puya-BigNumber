from algopy import (
    arc4,
    Bytes,
)
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
from puya_bignumber import barrett_reducer_factor


class BignumberTester(arc4.ARC4Contract):
    @arc4.abimethod()
    def add(self, a: Bytes, b: Bytes) -> Bytes:
        return add(a, b)

    @arc4.abimethod()
    def subtract(self, a: Bytes, b: Bytes) -> Bytes:
        return subtract(a, b)

    @arc4.abimethod()
    def equal(self, a: Bytes, b: Bytes) -> bool:
        return equal(a, b)

    @arc4.abimethod()
    def multiply(self, a: Bytes, b: Bytes) -> Bytes:
        return multiply(a, b)

    @arc4.abimethod()
    def divide(self, a: Bytes, b: Bytes) -> Bytes:
        return divide(a, b)

    @arc4.abimethod()
    def less_than(self, a: Bytes, b: Bytes) -> bool:
        return less_than(a, b)

    @arc4.abimethod()
    def greater_than(self, a: Bytes, b: Bytes) -> bool:
        return greater_than(a, b)

    @arc4.abimethod()
    def mod_barrett_reduce(self, a: Bytes, b: Bytes, c: Bytes) -> Bytes:
        return mod_barrett_reduce(a, b, c)

    @arc4.abimethod()
    def barrett_reducer_factor(self, a: Bytes) -> Bytes:
        return barrett_reducer_factor(a)

    @arc4.abimethod()
    def modexp_barrett_reduce(self, a: Bytes, b: Bytes, c: Bytes, d: Bytes) -> Bytes:
        return modexp_barrett_reduce(a, b, c, d)

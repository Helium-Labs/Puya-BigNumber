# Puya BigNumber

A library for mathematical operations involving (very) large numbers in Puya for Algorand. It supports addition, subtraction, multiplication, division, comparison, remainder calculation (using Barrett Reduction), and modular exponentiation (using Barrett Reduction) of large big-endian encoded numbers as byte strings. The library is implemented using some of the most efficient algorithms available in the literature, such as Karatsuba multiplication, Algorithm D by Donald Knuth for multi-word division, and Barrett Reduction for remainder calculation.

## Features

- Supports up to `1024 bytes` (8192 bits) wide numbers
- Algorand Puya smart contract HLL compatibility
- Algorand-python-testing framework

 Features the following operators:
- **Addition**: `O(n)` time complexity with 512 bit sized digits
- **Subtraction**: `O(n)` time complexity with 512 bit sized digits
- **Multiplication**: `O(n**1.58)` time complexity (Karatsuba multiplication) with 512 bit sized digits
- **Division**: `O(n*m)` time complexity (Algorithm D by Donald Knuth) with 256 bit sized digits
- **Remainder with Barrett Reduction**: `O(n**1.58)` time complexity with 512 bit sized digits
- **Modular Exponentiation with Barrett Reduction**: `O(exp.bit_length x n**1.58)` time complexity with 512 bit sized digits
- **Less than, greater than and equal comparison**: `O(max(n,m))` time complexity with 512 bit sized digits

In the above `n` and `m` refer to the number of digits in the input.

## Install

Puya BigNumber is available on PyPI:

```sh
pip install puya-bignumber
```

## Usage

All inputs to math functions are assumed to be big-endian encoded numbers unless explicitly stated otherwise.

```python
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
# ... use the functions as you might expect, e.g. add(big_endian_bytes_a, big_endian_bytes_b)
```

## Develop

This module uses `poetry` as the package manager and Python environment manager. Please see [How to Build and Publish Python Packages With Poetry](https://www.freecodecamp.org/news/how-to-build-and-publish-python-packages-with-poetry/).

### Test

```
poetry run pytest -v
```

## License & Contribution

Contributions and additions are welcomed. Please respect the terms of the [GNU GPL v3 license](./LICENSE). Attribution for the author _Winton Nathan-Roberts_ is required. No warranties or liabilities per the license. It is not yet officially production ready, although it is thoroughly tested.

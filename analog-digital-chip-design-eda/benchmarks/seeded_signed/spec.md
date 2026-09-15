# Seeded signed arithmetic benchmark

Signed four-bit operands are added with a five-bit signed result.

REQ-SIGNED-ADD: `a=-1` and `b=-1` produce `sum=-2`.

The RTL intentionally zero-extends negative operands.

# Seeded parity benchmark

After reset, `even` is high when the input word contains an even number of
one bits.

REQ-PARITY-EVEN: data `4'b0011` produces `even=1`.

The RTL intentionally inverts the parity result.

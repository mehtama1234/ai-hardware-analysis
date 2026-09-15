# Seeded arbiter benchmark

The arbiter returns a one-hot grant matching the active request after reset.

REQ-ARB-ONEHOT: with reset released and request `2'b10`, grant is `2'b10`.

The RTL intentionally ignores requester 1.

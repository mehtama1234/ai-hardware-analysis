# Seeded arbiter assertion-matrix specification

This matrix fixture preserves the arbiter mapping requirement and adds an
explicit structural safety requirement for the generated assertion path.

REQ-ARB-ONEHOT: with reset released and request `2'b10`, grant is `2'b10`.

REQ-ARB-ONEHOT-PREDICATE: grant is one-hot-or-zero.

REQ-ARB-MUTUAL-EXCLUSION: grant_a and grant_b are never high.

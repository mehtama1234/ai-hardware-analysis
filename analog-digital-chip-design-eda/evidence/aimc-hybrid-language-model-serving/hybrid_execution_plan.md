# Small Language-Model Serving Package

This package exercises the serving partition for a normalized decoder-transformer shape.

- scenarios: `5`
- operators: `14`
- analog projection candidates: `6`
- digital/SRAM operators: `8`
- scenario policy replay: `pass`
- physical converter gate: `blocked_sar_source_common_mode`

The package keeps token lookup, causal masking, Softmax, changing KV-cache reads/writes, value mixing, residuals, and normalization on digital/SRAM support. Fixed projections are analog candidates only when reuse and state-error policy allow it.

This includes a synthetic next-token quality rehearsal when the local task artifact is present. It is not a pretrained language-model quality result; the compiler and cost-policy portion is derived from normalized serving scenarios.

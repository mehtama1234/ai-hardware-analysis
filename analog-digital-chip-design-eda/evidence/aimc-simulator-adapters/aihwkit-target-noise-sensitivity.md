# AIHWKIT Target Noise Sensitivity

This replay keeps the 10-bit input and 12-bit output target fixed, then adds explicit output noise.

- target input bits: `10`
- target output bits: `12`
- rows per noise setting: `16`
- noise settings: `4`
- all-pass noise settings: `3`
- highest all-pass output noise: `0.004`
- passes any nonzero noise: `True`

## Noise Summary

| output noise | passing rows | failing rows | max residual | worst row | pass all |
| ---: | ---: | ---: | ---: | --- | --- |
| 0.000 | 16 | 0 | 0.043358 | deep_transformer_mlp_stack/block1.out.matmul | True |
| 0.001 | 16 | 0 | 0.049114 | deep_transformer_mlp_stack/block0.down.matmul | True |
| 0.004 | 16 | 0 | 0.102023 | deep_transformer_mlp_stack/block1.out.matmul | True |
| 0.012 | 10 | 6 | 0.251057 | deep_transformer_mlp_stack/block1.down.matmul | False |

## First-Principles Reading

The converter target solved one problem: it made the input and output bins fine enough. This replay asks a different question: how much output disturbance can the same target tolerate before the model-facing residual crosses the claim boundary again.

Output noise matters because it is added after the analog sum. At that point the row voltages and conductance products have already collapsed into a column value. A small output disturbance can be harmless when the column value is far from a decision edge, and damaging when two states need to remain separated.

A zero-noise pass is therefore not enough for hardware. A usable analog boundary needs a nonzero noise budget. If only the zero-noise case passes, the target is fragile. If small nonzero cases pass, the next circuit proof has a concrete noise allowance to try to meet.

## Refused Claim

does not prove measured noise, circuit noise, calibrated silicon, board accuracy, or production readiness

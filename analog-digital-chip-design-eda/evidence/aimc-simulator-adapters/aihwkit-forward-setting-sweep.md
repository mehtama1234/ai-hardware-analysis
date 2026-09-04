# AIHWKIT Forward Setting Sweep

This sweep asks which AIHWKIT non-perfect forward settings move the same MatMul rows across the positive residual boundary.

It does not change the importer threshold. It changes only the simulator-side forward assumptions and records the result.

- rows checked per setting: `16`
- settings checked: `5`
- best passing setting: `ideal_resolution_no_output_noise`
- best max residual: `0.000000119`

## Setting Summary

| setting | passing rows | failing rows | max residual | worst row | pass all |
| --- | ---: | ---: | ---: | --- | --- |
| baseline_nonperfect_no_noise_model | 0 | 16 | 1.515913 | deep_transformer_mlp_stack/block1.gate.matmul | False |
| no_output_noise | 9 | 7 | 0.330081 | deep_transformer_mlp_stack/block0.down.matmul | False |
| fine_resolution_no_output_noise | 16 | 0 | 0.043358 | deep_transformer_mlp_stack/block1.out.matmul | True |
| fine_resolution_large_bounds | 16 | 0 | 0.094221 | deep_transformer_mlp_stack/block1.out.matmul | True |
| ideal_resolution_no_output_noise | 16 | 0 | 0.000000 | deep_transformer_mlp_stack/block2.down.matmul | True |

## First-Principles Reading

The matrix object was already proven correct under ideal forward. This sweep keeps that object fixed and changes how the analog forward path limits the signal.

Output noise is the largest visible lever in this local test. Removing it makes the attention rows pass, and tighter converter resolution makes both attention and deep-stack rows much closer to the digital reference. Disabling input/output resolution limits drives the residual near floating-point tolerance while still using the AIHWKIT analog layer path.

That gives the next real design question: which of these simulator-side assumptions corresponds to a physically defensible analog tile? The answer cannot be claimed from this sweep alone; it needs a device, converter, and calibration story.

## Refused Claim

This sweep does not prove measured silicon, measured board runtime, measured power, PCM device accuracy, macro layout, or production readiness. It does not allow the importer threshold to be weakened.

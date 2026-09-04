# AIHWKIT Residual Diagnostic

This report explains why AIHWKIT is run evidence but not broad positive simulator evidence yet.

- payloads checked: `10`
- passing payloads: `3`
- threshold-fail payloads: `7`

## Fixture Summary

| fixture | status | estimated drop | candidates | over threshold | diagnosis |
| --- | --- | ---: | ---: | ---: | --- |
| small_fixture | pass | 0.052241 | 0 | 0 | inside the current positive residual boundary |
| workload_shape | pass | 0.090004 | 0 | 0 | inside the current positive residual boundary |
| tensor_shape | pass | 0.075669 | 2 | 0 | inside the current positive residual boundary |
| trained_weight_tiny_mlp | threshold_fail | 0.284556 | 2 | 1 | 1 candidate rows exceed the positive residual boundary |
| projection_stack | threshold_fail | 0.555104 | 4 | 4 | 4 candidate rows exceed the positive residual boundary |
| transformer_mlp_block | threshold_fail | 0.619054 | 4 | 4 | 4 candidate rows exceed the positive residual boundary |
| calibrated_transformer_mlp_block | threshold_fail | 0.624664 | 4 | 4 | 4 candidate rows exceed the positive residual boundary |
| calibrated_deep_transformer_mlp_stack | threshold_fail | 0.869884 | 12 | 9 | 9 candidate rows exceed the positive residual boundary |
| attention_block | threshold_fail | 0.916745 | 4 | 4 | 4 candidate rows exceed the positive residual boundary |
| calibrated_attention_block | threshold_fail | 0.609983 | 4 | 4 | 4 candidate rows exceed the positive residual boundary |

## Worst Candidate Rows

| fixture | candidate | shape | residual |
| --- | --- | --- | ---: |
| attention_block | attn.out.matmul | [8, 8] | 0.916745 |
| calibrated_deep_transformer_mlp_stack | block0.down.matmul | [64, 32] | 0.869884 |
| calibrated_deep_transformer_mlp_stack | block2.out.matmul | [32, 32] | 0.662175 |
| calibrated_deep_transformer_mlp_stack | block1.down.matmul | [64, 32] | 0.651986 |
| calibrated_deep_transformer_mlp_stack | block1.out.matmul | [32, 32] | 0.641421 |
| calibrated_transformer_mlp_block | mlp.down.matmul | [32, 16] | 0.624664 |
| transformer_mlp_block | mlp.down.matmul | [32, 16] | 0.619054 |
| calibrated_attention_block | attn.out.matmul | [8, 8] | 0.609983 |
| projection_stack | proj.v.matmul | [16, 12] | 0.555104 |
| calibrated_deep_transformer_mlp_stack | block2.up.matmul | [32, 64] | 0.551463 |
| calibrated_deep_transformer_mlp_stack | block1.gate.matmul | [32, 64] | 0.510856 |
| calibrated_deep_transformer_mlp_stack | block2.gate.matmul | [32, 64] | 0.493877 |

## First-Principles Reading

AIHWKIT is not failing because the importer is too strict. It is failing because several fixed-weight MatMul rows produce output vectors that move too far from the digital reference under the current AIHWKIT mapping.

The object to repair is the mapping from a signed weight matrix and input vector into the analog layer. Scaling, conductance range, noise settings, calibration, and output correction all change that mapping. The guarded threshold should not be changed to make the result look better.

A useful next experiment changes one mapping assumption, reruns the same held-out payloads, and checks whether the worst candidate rows move under the threshold without weakening the evidence rule.

## Refused Claim

This diagnostic does not turn threshold-fail AIHWKIT payloads into positive analog placement evidence. It does not prove calibrated silicon, measured board runtime, measured power, macro layout, or production readiness.

# Tiny Transformer Integration Report

Generated: `2026-08-31T01:53:07.913906+00:00`
Cases: `3`

| case | shape | status | max abs error | grad error | fused median s | tokens/s |
|---|---|---|---:|---:|---:|---:|
| chat-prefill-small | 2x16x64 h=4 | passed | 1.19209e-07 | 4.65661e-10 | 0.00300104 | 10662.9773 |
| decode-window-medium | 2x32x128 h=4 | passed | 1.19209e-07 | 2.03727e-10 | 0.00560933 | 11409.5684 |
| long-context-proxy | 1x64x128 h=4 | passed | 1.19209e-07 | 1.16415e-10 | 0.00567715 | 11273.2581 |

## Selected Autotune Records

- `matmul`: `{'record_id': 'matmul-128', 'shape_class': 'medium-square', 'config_id': 'tensorcore-64x64x32', 'estimated_speedup_vs_measured': 1.3889}`
- `normalization`: `{'record_id': 'softmax-4x1024', 'shape_class': 'wide', 'config_id': 'persistent-row', 'estimated_speedup_vs_measured': 1.3514}`
- `custom-op`: `{'record_id': 'custom-op-decoder-hidden', 'shape_class': 'decoder-hidden', 'config_id': 'fused-forward-backward', 'estimated_speedup_vs_measured': 1.4286}`

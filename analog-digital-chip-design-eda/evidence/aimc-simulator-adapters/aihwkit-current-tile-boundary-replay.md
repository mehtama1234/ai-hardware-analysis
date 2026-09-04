# AIHWKIT Current Tile Boundary Replay

This replay runs AIHWKIT with the current local tile converter boundary instead of a stronger sweep setting.

- tile DAC bits: `4`
- tile ADC bits: `6`
- rows checked: `16`
- passing rows: `0`
- failing rows: `16`
- max residual: `1.000000`
- worst row: `deep_transformer_mlp_stack/block0.down.matmul`

## Rows

| fixture | candidate | shape | residual | pass |
| --- | --- | --- | ---: | --- |
| attention_block | attn.q.matmul | [8, 8] | 0.422950 | False |
| attention_block | attn.k.matmul | [8, 8] | 0.375675 | False |
| attention_block | attn.v.matmul | [8, 8] | 0.373555 | False |
| attention_block | attn.out.matmul | [8, 8] | 0.975279 | False |
| deep_transformer_mlp_stack | block0.gate.matmul | [32, 64] | 0.352811 | False |
| deep_transformer_mlp_stack | block0.up.matmul | [32, 64] | 0.361450 | False |
| deep_transformer_mlp_stack | block0.down.matmul | [64, 32] | 1.000000 | False |
| deep_transformer_mlp_stack | block0.out.matmul | [32, 32] | 0.585126 | False |
| deep_transformer_mlp_stack | block1.gate.matmul | [32, 64] | 1.000000 | False |
| deep_transformer_mlp_stack | block1.up.matmul | [32, 64] | 1.000000 | False |
| deep_transformer_mlp_stack | block1.down.matmul | [64, 32] | 1.000000 | False |
| deep_transformer_mlp_stack | block1.out.matmul | [32, 32] | 1.000000 | False |
| deep_transformer_mlp_stack | block2.gate.matmul | [32, 64] | 0.725273 | False |
| deep_transformer_mlp_stack | block2.up.matmul | [32, 64] | 0.901072 | False |
| deep_transformer_mlp_stack | block2.down.matmul | [64, 32] | 0.753919 | False |
| deep_transformer_mlp_stack | block2.out.matmul | [32, 32] | 1.000000 | False |

## First-Principles Reading

A tile boundary is a promise about finite decisions. A 4-bit DAC has only sixteen input levels. A 6-bit ADC has only sixty-four output levels. If the model row needs finer distinctions than those bins preserve, the analog result moves away from the digital reference.

This replay keeps the strict residual threshold and asks what the current tile boundary does. It is the honest counterpart to the stronger forward-setting sweep.

## Refused Claim

This replay does not prove measured silicon, measured board runtime, measured power, macro layout, PCM device accuracy, or production readiness. It does not turn failing rows into placement evidence.

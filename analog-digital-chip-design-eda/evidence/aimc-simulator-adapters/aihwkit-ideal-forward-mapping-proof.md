# AIHWKIT Ideal Forward Mapping Proof

This proof separates two questions that were previously mixed together.

First question: are the layer dimensions, weight orientation, and signed MatMul object mapped correctly into AIHWKIT? Yes, under an explicit perfect-forward AIHWKIT configuration, the tested MatMul rows reproduce the digital reference within floating-point tolerance.

Second question: do the same rows pass under AIHWKIT's non-perfect inference path with its default input/output behavior and PCM-like assumptions? No. That remains the mapping work item.

- rows checked: `16`
- fixtures checked: `2`
- maximum ideal-forward residual: `0.000000091`
- passing rows under ideal-forward boundary: `16`

## Rows

| fixture | candidate | shape | residual |
| --- | --- | --- | ---: |
| attention_block | attn.q.matmul | [8, 8] | 0.000000053 |
| attention_block | attn.k.matmul | [8, 8] | 0.000000062 |
| attention_block | attn.v.matmul | [8, 8] | 0.000000062 |
| attention_block | attn.out.matmul | [8, 8] | 0.000000070 |
| deep_transformer_mlp_stack | block0.gate.matmul | [32, 64] | 0.000000084 |
| deep_transformer_mlp_stack | block0.up.matmul | [32, 64] | 0.000000073 |
| deep_transformer_mlp_stack | block0.down.matmul | [64, 32] | 0.000000064 |
| deep_transformer_mlp_stack | block0.out.matmul | [32, 32] | 0.000000075 |
| deep_transformer_mlp_stack | block1.gate.matmul | [32, 64] | 0.000000085 |
| deep_transformer_mlp_stack | block1.up.matmul | [32, 64] | 0.000000091 |
| deep_transformer_mlp_stack | block1.down.matmul | [64, 32] | 0.000000081 |
| deep_transformer_mlp_stack | block1.out.matmul | [32, 32] | 0.000000065 |
| deep_transformer_mlp_stack | block2.gate.matmul | [32, 64] | 0.000000076 |
| deep_transformer_mlp_stack | block2.up.matmul | [32, 64] | 0.000000081 |
| deep_transformer_mlp_stack | block2.down.matmul | [64, 32] | 0.000000062 |
| deep_transformer_mlp_stack | block2.out.matmul | [32, 32] | 0.000000080 |

## First-Principles Reading

A matrix multiply has three objects: the input vector, the stored weight matrix, and the output vector. If the weight is transposed incorrectly, or if the layer is built with the wrong input and output sizes, a perfect forward path will still produce the wrong vector.

This proof removes the analog forward imperfections and asks only whether AIHWKIT receives the same mathematical object as the digital reference. It does. That means the next repair should not chase orientation or shape. It should tune the non-perfect forward path: input range, converter resolution, output noise, conductance mapping, and calibration.

## Refused Claim

This proof does not make the default AIHWKIT payloads positive analog evidence. It does not prove PCM behavior, measured silicon, measured runtime, measured power, macro layout, or production readiness.

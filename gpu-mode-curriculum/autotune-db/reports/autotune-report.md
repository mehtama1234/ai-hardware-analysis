# Autotuning Database Report

Generated: `2026-09-07T23:00:36.819222+00:00`
Records: `18`
Families: `custom-op, fusion, matmul, memory, normalization, reduction`

| record | family | shape | selected config | status | measured s | estimated s | modeled speedup | targets |
|---|---|---|---|---|---:|---:|---:|---|
| vector-copy-contiguous-64k | memory | small | vectorized-128b | proposed_not_measured | 0.00528082 | 0.00433027 | 1.2195 | cuda, triton |
| vector-copy-contiguous-1m | memory | medium | vectorized-128b | proposed_not_measured | 0.03086989 | 0.02531331 | 1.2195 | cuda, triton |
| vector-copy-strided-64k-s4 | memory | strided | vectorized-128b | proposed_not_measured | 0.00068073 | 0.00055820 | 1.2195 | cuda, triton |
| vector-copy-strided-64k-s16 | memory | strided | vectorized-128b | proposed_not_measured | 0.03372995 | 0.02765856 | 1.2195 | cuda, triton |
| reduction-sum-max-128k | reduction | medium | warp-shuffle-tree | proposed_not_measured | 0.00044343 | 0.00034588 | 1.2821 | cuda, triton |
| reduction-sum-max-1m | reduction | large | warp-shuffle-tree | proposed_not_measured | 0.01902599 | 0.01484027 | 1.2821 | cuda, triton |
| softmax-8x256 | normalization | narrow | persistent-row | proposed_not_measured | 0.00136030 | 0.00100662 | 1.3514 | cuda, triton |
| softmax-4x1024 | normalization | wide | persistent-row | proposed_not_measured | 0.00010510 | 0.00007777 | 1.3514 | cuda, triton |
| layernorm-8x256 | normalization | narrow | persistent-row | proposed_not_measured | 0.00030033 | 0.00022224 | 1.3514 | cuda, triton |
| layernorm-4x1024 | normalization | wide | persistent-row | proposed_not_measured | 0.00019949 | 0.00014762 | 1.3514 | cuda, triton |
| matmul-64 | matmul | small-square | tensorcore-64x64x32 | proposed_not_measured | 0.00070078 | 0.00050456 | 1.3889 | cuda, triton |
| matmul-128 | matmul | medium-square | tensorcore-64x64x32 | proposed_not_measured | 0.00297278 | 0.00214040 | 1.3889 | cuda, triton |
| fused-mlp-16x128 | fusion | small-hidden | single-program-hidden | proposed_not_measured | 0.00089765 | 0.00068221 | 1.3158 | cuda, triton |
| fused-mlp-8x256 | fusion | medium-hidden | single-program-hidden | proposed_not_measured | 0.00116861 | 0.00088814 | 1.3158 | cuda, triton |
| custom-op-small-mlp | custom-op | small-mlp | fused-forward-backward | proposed_not_measured | 0.00043330 | 0.00030331 | 1.4286 | torch-extension, cuda |
| custom-op-decoder-hidden | custom-op | decoder-hidden | fused-forward-backward | proposed_not_measured | 0.00069980 | 0.00048986 | 1.4286 | torch-extension, cuda |
| custom-op-wide-ffn | custom-op | wide-ffn | fused-forward-backward | proposed_not_measured | 0.00139210 | 0.00097447 | 1.4286 | torch-extension, cuda |
| custom-op-bf16-transformer | custom-op | bf16-transformer | fused-forward-backward | proposed_not_measured | 0.00065105 | 0.00045573 | 1.4286 | torch-extension, cuda |

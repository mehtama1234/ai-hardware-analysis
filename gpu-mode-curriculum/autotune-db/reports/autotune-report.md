# Autotuning Database Report

Generated: `2026-08-31T01:53:04.837042+00:00`
Records: `18`
Families: `custom-op, fusion, matmul, memory, normalization, reduction`

| record | family | shape | selected config | measured s | estimated s | speedup | targets |
|---|---|---|---|---:|---:|---:|---|
| vector-copy-contiguous-64k | memory | small | vectorized-128b | 0.00035776 | 0.00029336 | 1.2195 | cuda, triton |
| vector-copy-contiguous-1m | memory | medium | vectorized-128b | 0.00435604 | 0.00357195 | 1.2195 | cuda, triton |
| vector-copy-strided-64k-s4 | memory | strided | vectorized-128b | 0.00028816 | 0.00023629 | 1.2195 | cuda, triton |
| vector-copy-strided-64k-s16 | memory | strided | vectorized-128b | 0.00051647 | 0.00042351 | 1.2195 | cuda, triton |
| reduction-sum-max-128k | reduction | medium | warp-shuffle-tree | 0.00037910 | 0.00029570 | 1.2821 | cuda, triton |
| reduction-sum-max-1m | reduction | large | warp-shuffle-tree | 0.00198343 | 0.00154708 | 1.2821 | cuda, triton |
| softmax-8x256 | normalization | narrow | persistent-row | 0.00019314 | 0.00014292 | 1.3514 | cuda, triton |
| softmax-4x1024 | normalization | wide | persistent-row | 0.00008190 | 0.00006061 | 1.3514 | cuda, triton |
| layernorm-8x256 | normalization | narrow | persistent-row | 0.00025953 | 0.00019205 | 1.3514 | cuda, triton |
| layernorm-4x1024 | normalization | wide | persistent-row | 0.00017416 | 0.00012888 | 1.3514 | cuda, triton |
| matmul-64 | matmul | small-square | tensorcore-64x64x32 | 0.00016445 | 0.00011841 | 1.3889 | cuda, triton |
| matmul-128 | matmul | medium-square | tensorcore-64x64x32 | 0.00021118 | 0.00015205 | 1.3889 | cuda, triton |
| fused-mlp-16x128 | fusion | small-hidden | single-program-hidden | 0.00130725 | 0.00099351 | 1.3158 | cuda, triton |
| fused-mlp-8x256 | fusion | medium-hidden | single-program-hidden | 0.00096464 | 0.00073313 | 1.3158 | cuda, triton |
| custom-op-small-mlp | custom-op | small-mlp | fused-forward-backward | 0.00043330 | 0.00030331 | 1.4286 | torch-extension, cuda |
| custom-op-decoder-hidden | custom-op | decoder-hidden | fused-forward-backward | 0.00069980 | 0.00048986 | 1.4286 | torch-extension, cuda |
| custom-op-wide-ffn | custom-op | wide-ffn | fused-forward-backward | 0.00139210 | 0.00097447 | 1.4286 | torch-extension, cuda |
| custom-op-bf16-transformer | custom-op | bf16-transformer | fused-forward-backward | 0.00065105 | 0.00045573 | 1.4286 | torch-extension, cuda |

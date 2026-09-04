# Hybrid Attention Vertical Slice

This package separates static projection work from dynamic attention work.

- analog candidates: `4` static projection MatMuls (`Q`, `K`, `V`, output)
- digital support: `4` dynamic score, scale, Softmax, and value operations
- SRAM: token activations, Q/K/V buffers, score matrix, KV-cache placeholder, and fallback buffers
- CrossSim replay: `4.17733e-08` relative L2, pass `true`
- physical converter gate: `blocked_sar_source_common_mode`

The simulator result does not prove that a full transformer can run on the chip. Dynamic attention and cache movement remain digital until their timing, memory, and task-impact evidence exists.

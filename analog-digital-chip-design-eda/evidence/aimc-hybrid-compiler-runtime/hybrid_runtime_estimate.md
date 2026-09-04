# Hybrid Runtime Estimate

The target command schedule was checked for complete coverage, sequence ordering, and overlap.

- schedule verified: `true`
- models: `12`
- commands: `321`
- register writes: `368`
- serialized planning cost: `687` cycles
- analog tile commands: `46`
- converter commands: `92`
- SRAM commands: `92`
- digital support commands: `45`

## Digital-Only Planning Comparison

Each workload is compared with a deliberately simple digital-only planning baseline. This is useful for exposing converter and fallback overhead, but it is not measured latency, energy, or power.

- `attention-block`: hybrid `291` cycles versus digital-only `24` cycles; ratio `12.125`; converter commands `8`; guarded fallback commands `4`
- `camera-defect-classifier-intake`: hybrid `561` cycles versus digital-only `15` cycles; ratio `37.400`; converter commands `6`; guarded fallback commands `3`
- `compact-defect-classifier-intake`: hybrid `645` cycles versus digital-only `15` cycles; ratio `43.000`; converter commands `6`; guarded fallback commands `3`
- `deep-transformer-mlp-stack`: hybrid `231` cycles versus digital-only `48` cycles; ratio `4.812`; converter commands `24`; guarded fallback commands `12`
- `fusion-transformer-small-intake`: hybrid `603` cycles versus digital-only `15` cycles; ratio `40.200`; converter commands `6`; guarded fallback commands `3`
- `keyword-detector-v3-intake`: hybrid `519` cycles versus digital-only `18` cycles; ratio `28.833`; converter commands `8`; guarded fallback commands `4`
- `projection-stack`: hybrid `75` cycles versus digital-only `21` cycles; ratio `3.571`; converter commands `8`; guarded fallback commands `4`
- `small-language-model-serving-shape-v1`: hybrid `465` cycles versus digital-only `42` cycles; ratio `11.071`; converter commands `12`; guarded fallback commands `6`
- `tiny-mlp`: hybrid `18` cycles versus digital-only `18` cycles; ratio `1.000`; converter commands `0`; guarded fallback commands `0`
- `transformer-mlp-block`: hybrid `351` cycles versus digital-only `24` cycles; ratio `14.625`; converter commands `8`; guarded fallback commands `4`
- `vla-policy-intake`: hybrid `687` cycles versus digital-only `15` cycles; ratio `45.800`; converter commands `6`; guarded fallback commands `3`
- `wake-nonwake-mlp`: hybrid `369` cycles versus digital-only `18` cycles; ratio `20.500`; converter commands `0`; guarded fallback commands `0`

These are schedule estimates, not observed runtime or energy. The physical converter gate remains blocked by high-code threshold compression.

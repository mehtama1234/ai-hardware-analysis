# Language-Model Serving Task Rehearsal

- status: `synthetic_token_quality_rehearsal_pass`
- profile: `educational-hybrid-tile-v1`
- dataset: `language-model-serving-token-rehearsal-v1`
- records: `16`
- baseline next-token accuracy: `1.0000`
- candidate next-token accuracy: `0.9375`
- drop: `0.0625`
- tolerance: `0.1000`
- pass: `True`

The candidate applies one controlled projection error to exercise the token decision boundary. The dataset is synthetic and deterministic; this is a serving-path rehearsal, not pretrained-model evidence.

Refused claim: pretrained language-model quality, real corpus perplexity, measured token latency or energy, board runtime, silicon, or production readiness

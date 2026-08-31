# Speculative Decoding Serving

## First Question

A small draft model can propose tokens faster than a large target model. The target model still must verify the tokens. This lane asks when accepted draft tokens reduce total decode work and when rejected tokens add waste.

## What The Code Does

- `speculative-decoding-serving/speculative_decoding_serving/analyzer.py computes acceptance, rollback, wasted draft tokens, and speedup.`
- `scripts/run_speculative_decoding_serving.py writes the report.`
- `gpu-runs/gpu_runs/collector.py imports the Colab measured status for this step.`

## What The Measurement Proves

The measurement proves the system records both the good case and the bad case. It accepts high speedup only when acceptance and waste are visible.

## What It Does Not Prove

It does not prove a specific draft model is the best choice. It proves the scheduler can be judged by acceptance rate, wasted work, and output speed.

## Read Next

- `site/speculative-decoding-serving.html`
- `lesson-labs/lesson-096-lecture-22-hacker-s-guide-to-speculative-decoding-in-vllm/README.md`

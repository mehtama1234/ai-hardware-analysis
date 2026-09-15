# Real-Model Inference Decision Vertical Slice

## Meaty goal

Take one real pretrained causal language model from model intake through
tokenization, baseline inference, optimized serving, measured accelerator
behavior, quality checks, and a final hardware decision.

The result must answer:

> For this workload, what is the dominant bottleneck, did the optimization
> improve end-to-end behavior, and is there a defensible reason to pursue a
> hybrid analog/digital implementation?

## End-to-end path

```text
real model + tokenizer
  -> trusted baseline
  -> optimized/serving path
  -> prefill and decode measurements
  -> KV-cache, batching, admission, cancellation, and tail behavior
  -> output quality and correctness comparison
  -> operator and data-movement cost breakdown
  -> bounded analog/hybrid candidate analysis
  -> claim-safe decision package
```

## Required inputs

- A pretrained model with a real tokenizer and an identified revision or file
  hash.
- A small, fixed evaluation/prompts fixture with provenance.
- One trusted baseline and one candidate serving path.
- One real accelerator run, beginning with the already-used T4 path when
  available.
- The existing analog hardware profile, used only to analyze candidate fixed
  weight projections until extracted converter evidence exists.

## Required evidence

Each run must preserve the command, source identity, model/tokenizer identity,
device, runtime versions, workload shapes, warm-up, repetitions,
synchronization, raw samples, correctness result, and artifact hashes.

The package must contain, at minimum:

- model and tokenizer intake;
- baseline/candidate output parity or a measured quality comparison;
- separate prefill and decode latency distributions;
- KV-cache and memory accounting;
- concurrency and tail-latency results;
- explicit conversion, fallback, and data-movement costs;
- measured accelerator evidence, clearly separated from modeled energy;
- analog candidate rows with a break-even calculation;
- allowed claims, refused claims, and the next required measurement.

## Completion rule

This goal is complete only when the final package can state one of these
outcomes for the selected workload:

1. the candidate improves the real end-to-end workload under the stated
   conditions;
2. the candidate does not improve it, with the measured bottleneck identified;
3. the evidence is insufficient, with the exact missing measurement named.

Synthetic character models, replayed vectors, Python reference timing, starter
layout area, and modeled pJ coefficients may support preparation, but they do
not close this goal.

## Current starting point

The repository already has measured T4 serving and trained-quality artifacts,
but those artifacts are explicitly scoped to a synthetic character-transformer
workload. The current local software environment lacks PyTorch and
Transformers, so the next execution handoff is to a GPU-capable environment
with the real model and tokenizer dependencies installed. The blocked analog
post-layout candidate remains a downstream evidence lane and must not block the
model-level decision package.

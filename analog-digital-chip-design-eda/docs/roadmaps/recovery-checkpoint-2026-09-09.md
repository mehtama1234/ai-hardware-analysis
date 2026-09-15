# Recovery checkpoint — 2026-09-09

Recovered from Git history, uncommitted source, and saved experiment results.
This is a review checkpoint, not a new simulation or accelerator run. The
session goal service returned no active goal; the objective below is recovered
from repository documents and recent implementation.

## Goal and latest direction

The overarching goal connects model intake, hybrid compilation/runtime,
physical converter evidence, and a fair task-level digital/hybrid comparison.
See `../research/combined-aimc-workbench-end-to-end-goal.md`.

The newer immediate goal is the sibling project's
`software-architecture/real-model-inference-decision-goal.md`: take a real
pretrained causal model through measured serving and produce a defensible
hardware decision. A negative optimization result is a valid outcome. Analog
physical closure is a separate evidence lane and does not block that decision.

## Latest software work

The newest source edits found were on September 9 at approximately 04:44–04:46
America/Los_Angeles, in `build_real_model_architecture_decision.py`,
`run_transformer_vertical_slice.py`,
`build_real_model_workload_hardware_contract.py`, and
`check_real_model_decision_package.py` under the sibling software scripts.
They integrate serving verdicts, SDPA evidence, digital memory/compute
denominators, and the recommendation to retain native serving.

Saved reports under `gpu-mode-curriculum/gpu-runs/imports/` show:

| Run directory | Recorded result |
| --- | --- |
| `colab-real-model-fused-append-cache-gpt2-20260909-r2` | Exact output parity; native scheduled median 383.243 ms, persistent candidate 482.481 ms, about 26% slower; 8 generated tokens, 5 repetitions |
| `colab-real-model-persistent-page-cache-long-gpt2-20260909` | Exact output parity; native scheduled median 1526.172 ms, persistent candidate 2189.583 ms, about 43% slower; 64 generated tokens, 3 repetitions |
| `colab-real-model-sdpa-backend-gpt2-20260909` | Output parity; eager median 688.458 ms, SDPA 694.663 ms; SDPA not proven better |

These are bounded GPT-2/Tesla-T4 observations. The NVML reports explicitly
limit their power scope; they do not establish isolated energy per token or
analog benefit. Comparisons against independent singles must not replace the
native scheduled baseline when deciding whether to promote the custom kernel.

## Latest EDA stopping point

The newest saved run is
`evidence/aimc-simulator-adapters/active-converter-macro-transient/20260909T075601726677Z/result.json`
(completed about 00:56 local time). It uses the
`active-converter-macro-candidate/physical-integrated-tail-local-final` candidate.
All eight simulations completed, and all eight met the runner's logic-margin
criterion. Only one met its polarity criterion; that one is the zero-differential
case. All seven negative-differential cases failed, with nearly identical output
polarity. The run explicitly has `accepted_converter: false`.

The saved netlist SHA-256 is
`9992572bdc570d66c69e3e0d67993b799d907989ec34a09ed7fb2f600dd62417`.
This review has not independently revalidated that hash or rerun the circuit.
Strong output swing therefore does not establish a functioning comparator.
The electrical failure mechanism still needs diagnosis. Full SAR correctness,
PVT, mismatch/noise, and accepted post-layout evidence remain open.

## Resume point

1. Reconstruct a durable final real-model package from the saved GPU imports,
   including the short/long persistent-cache comparisons and SDPA comparison.
   Run `check_real_model_decision_package.py` against it and inspect that the
   final architecture decision retains native digital serving and blocks analog.
   No matching real-model/transformer output directory was found directly under
   `/tmp` during recovery; a completed latest package has not been verified.
2. Refresh outdated README statements from that checked package. The software
   README still points to page packing as the next bottleneck; newer source
   incorporates the direct-K/V diagnostic and recommends against promotion.
   The EDA README's microvolt-margin description predates the latest failed
   polarity experiment.
3. For the EDA lane, inspect extracted connectivity, initialization, timing,
   and polarity conventions on this exact candidate before further design
   changes. Preserve the failed run. Do not treat layout checks or output swing
   as converter acceptance.

The last commits affecting these projects were September 6 checkpoints
`ea7b01ad` and `a1e85206`. Substantial later code and results are uncommitted,
including GPU work outside the two named directories. No matching ngspice,
Magic, transformer-package, or Colab-handoff process was found during review.
No source or existing evidence was changed by this recovery review.

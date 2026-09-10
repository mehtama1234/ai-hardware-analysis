# Crash recovery checkpoint — 2026-09-09

Reconstructed from goal documents, Git history, working-tree changes, runner
source, and imported reports. This records repository evidence, not recovered
conversation history. GPU experiments were not rerun during recovery.

Subsequent implementation and GPU runs are recorded in the
[active real-model checkpoint](batch1-decode-vertical-slice/END-TO-END-GOAL.md).
The sections below retain the state as it was first recovered.

## End-to-end goal

The overarching [advanced curriculum goal](advanced-lab-phase/END-TO-END-GOAL.md)
is: mathematical reference → correct kernel → measured optimization → model
integration → profiler explanation → tutorial/workbench recommendation.
The original [meaty goal](MEATY-GOAL.md) supplies the GPUMODE transcript,
curriculum, paper, and runnable-lab infrastructure.

The latest implementation follows the adjacent
[real-model inference decision goal](../analog-in-memory-ai-inference/software-architecture/real-model-inference-decision-goal.md):
pretrained model/tokenizer → trusted baseline → optimized serving → prefill,
decode, memory, concurrency, cancellation, quality, and movement measurements
→ bounded analog/hybrid analysis → evidence-backed decision package.
The hardware analysis is downstream; missing physical analog evidence must not
block an honest model-level decision.

## Where work stopped

Latest committed history includes trained T4 end-to-end evidence, corrected
acceptance/reproduction, broader imported coverage, and multi-GPU/ROCm handoff
(`80969d12`). Substantial subsequent real-model work remains untracked, with
tracked changes in the Colab runners and handoff README.

The real-model sequence under `batch1-decode-vertical-slice/` progresses through
GPT-2 baseline characterization, candidate comparison, microbatching, bounded
arrival grouping/cancellation, paged-cache adaptation, custom CUDA attention,
full-model fused decode, device-resident workspace reuse, direct-KV controls,
persistent per-layer page caches, and a native SDPA comparison.

The latest runner modification and imported directory by filesystem timestamp
are `run_real_model_sdpa_backend.py` and
`gpu-runs/imports/colab-real-model-sdpa-backend-gpt2-20260909/`.
Older summary READMEs predate this work and do not describe the latest state.

## Last recorded results

These are recorded report values, not independently reproduced acceptance.

| Imported run | Native scheduled median | Custom scheduled median | Finding |
| --- | ---: | ---: | --- |
| `colab-real-model-device-resident-arrival-load-workspace-reuse-gpt2-20260909-r2` | 481.37 ms | 520.47 ms | Reported token parity; custom remains slower |
| `colab-real-model-fused-append-cache-gpt2-20260909-r2` | 383.24 ms | 477.07 ms; persistent 482.48 ms | All three reported parity checks pass; custom remains slower |
| `colab-real-model-persistent-page-cache-long-gpt2-20260909` | 1526.17 ms | 2104.74 ms; persistent 2189.58 ms | All three reported parity checks pass; custom remains slower |

The long-decode run records native sequential latency of 4472.82 ms. Its
reported 2.13x custom speedup compares against sequential execution. It does
not establish a custom-kernel improvement over native scheduled execution.

The final SDPA report records exact token parity and medians of 688.46 ms
for the baseline and 694.66 ms for SDPA, with decision
`native_sdpa_backend_not_proven_better` (five repeats, 64 new tokens, T4).
However, the baseline loader does not explicitly set `attn_implementation="eager"`.
The selected backend is not recorded, so a distinct eager-versus-SDPA comparison
is not established by that report alone.

## Concrete continuation

1. Harden the latest real-model report acceptance before further optimization:
   require all applicable parity checks, derive acceptance from checks rather
   than unconditional flags, retain model/tokenizer revisions and source hashes,
   and report custom/native-scheduled ratios alongside sequential comparisons.
2. Explicitly select and record both attention backends for a valid SDPA control;
   preserve existing raw reports and use a new run ID for a corrected experiment.
3. Explain the custom-kernel regression using profiling of native scheduled and
   custom scheduled generation on identical workloads. Distinguish batching
   benefits from kernel benefits, and bounded offline arrival grouping from a
   live continuous-batching serving system.
4. Reconcile the accumulated evidence into the decision package and curriculum
   checkpoint/site. A supported negative optimization result is a valid outcome.
   Keep production quality, serving capacity, multi-GPU/ROCm, and physical analog
   claims open until their specific measurements exist.

The broader repository contains unrelated analog/EDA modifications. Preserve
them and the untracked real-model source/configuration/report files.

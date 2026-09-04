# Wake-Word Hybrid Execution Plan

This package runs the wake-word workload through the shared compiler schema and records a digital placement decision even though the dense layers are analog candidates.

- operators: `6`
- selected analog operators: `0`
- analog candidates retained for review: `2`
- task result: `wake_word_f1=1.0` on `24` generated samples
- cost decision: `digital_for_this_small_workload`
- physical converter gate: `blocked_sar_source_common_mode`

## Decision

The nominal analog error rehearsal preserves all wake/nonwake decisions, but the end-to-end cost model selects the digital path: hybrid latency is 41 versus 28 normalized units and hybrid energy is 154.2 versus 152.0. This is an explicit workload-dependent fallback decision, not evidence that analog is universally unsuitable.

## Claim Boundary

The workload uses generated audio rather than a field dataset and has no board or silicon trace. The package proves placement reasoning and task/cost handoff only.

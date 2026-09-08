# Distributed evidence audit

This is a source-level audit of existing work, not a new execution result.

## Collectives: execution path exists, acceptance is insufficient

[`benchmark.py`](../distributed-collectives/distributed_collectives/benchmark.py)
invokes torch.distributed all-reduce, all-gather, reduce-scatter, all-to-all and
broadcast. The stored [run report](../distributed-collectives/reports/collective-benchmark-run.json)
records `skipped:missing-accelerator`, world size one and no benchmark rows.
It does not establish successful multi-process execution.

Source-level gaps that must be closed before accepting a future run:

1. `_benchmarks.add` treats a returned timing call as `passed`, without comparing
   any output with an oracle or rejecting non-finite tensor values.
2. All-reduce repeatedly mutates `base` across warmups and iterations. Later
   all-gather/all-to-all/broadcast also reuse that mutated input. Reset inputs
   outside each measured sample and validate each operation independently.
3. `_time_ms` retains only one batch average; no raw repeat distribution or
   per-rank timings are recorded. Its ending barrier is inside the timed scope.
4. Any operation exception becomes `skipped`; three passed operations suffice
   for overall success. Unsupported capability must be distinguished from a
   broken operation, incorrect output or failed rank.
5. Requested byte counts are rounded to tensor element counts, and reduce-scatter
   rounds again for world size. Reports should record actual input/output bytes
   and explicit divisibility contracts instead of applying requested bytes to
   every operation's bandwidth calculation.
6. `aggregate_metrics.overlap_gain` comes from the scenario model, not measured
   concurrent compute/communication. `bandwidth_efficiency` falls back to the
   model on an unavailable run; otherwise it divides by a fixed 100 GB/s.
   These fields cannot establish measured overlap or topology efficiency.

Next execution gate: bounded two-process CPU/Gloo correctness with rank-specific
inputs and exact full-output checks, followed by independently accepted GPU
NCCL/RCCL execution. CPU execution must remain labeled CPU, and is not a waiver
of the multi-GPU requirement. Add process timeouts, collective capability handling,
raw samples, rank agreement, environment/source hashes and error-path tests.

The separate [collective analyzer](../distributed-collectives/distributed_collectives/analyzer.py)
computes transfer/latency/overlap estimates from declared scenario constants.
Its passed scenarios are model checks, not executions of the named backends.

## Executed follow-up: CPU latency baseline

`distributed-collectives/run_cpu_benchmark.py` now records five synchronized
samples per operation on two local Gloo ranks. Every sample uses fresh
rank-specific inputs and checks the complete output before retaining the timing;
the report keeps both rank-local raw samples and medians. This closes the local
baseline gap for latency measurement, but it intentionally does not change the
multi-GPU gate: no GPU bandwidth, overlap, topology, or NCCL/RCCL claim can be
derived from the CPU report.

## Topology: analytical planning

[`planner.py`](../distributed-topology/distributed_topology/planner.py) uses
fixed topology capacities/bandwidths and workload proxies. KV memory is estimated
from a parameter-count-derived hidden-size proxy; activation memory uses fixed
allowances. Strategies are ranked by modeled capacity and communication cost.
Generated `torchrun ... <tp-or-collective-benchmark>` commands are placeholders,
not completed reproductions. No measured topology discovery or application run
is established by a recommended configuration.

## MoE: routing-count simulation, not expert execution

[`simulator.py`](../moe-routing-all-to-all/moe_routing_all_to_all/simulator.py)
uses seeded random expert assignments to count loads, capacity drops and
fairness. Each top-k assignment is sampled independently: the same token can be
assigned to the same expert more than once. This is not a unique top-k router.
Communication time is calculated from payload and fabric constants; there are
no expert weight tensors, dispatch exchanges, expert matmuls or output combine.

Next gate: define unique top-k and capacity/drop semantics, implement a tensor
reference with dispatch/combine identity tests, then compare distributed outputs
against the reference. Measure imbalance and communication separately from
expert compute; retain both balanced and capacity-exceeding cases.

Primary-source review and hardware execution for these topics remain open.

## Executed follow-up: bounded CPU correctness

The new [two-process reference run](../distributed-collectives/CPU-CORRECTNESS.md)
passed all five operations on both CPU/Gloo ranks with full-output equality,
fresh rank-specific inputs and sentinel-filled receive buffers. This provides
local execution evidence independent of the old benchmark, without accepting
that benchmark's timings or mixed aggregate metrics. Broader shape/world-size
coverage, GPU execution, measured overlap and the MoE implementation remain open.

## Executed follow-up: MoE tensor reference

The [new CPU reference](../moe-routing-all-to-all/REFERENCE.md) implements unique
top-k, deterministic ties, explicit capacity drops, linear expert computation and
weighted combine. Four tests passed, including outputs and input/router/weight
gradients against a scalar oracle in eight dtype/routing/capacity combinations.
The original simulator remains unchanged; this addition does not establish
distributed expert dispatch, trained quality or GPU execution.

Subsequent [two-process experiment](../moe-routing-all-to-all/DISTRIBUTED.md)
executed padded all-to-all dispatch and return with sharded linear expert weights.
All sixteen rank/scenario comparisons passed with exact output and capacity-mask
agreement in the fixtures. Trained quality, distributed gradients, wider shapes,
efficient variable-size exchange, measured overlap and GPU execution remain open.

## Executed follow-up: distributed serving dispatch

`model-integration/run_distributed_serving_cpu.py` adds a two-rank Gloo serving
dispatch contract. Each rank owns a different request subset, exchanges result
objects, and independently checks rank ownership, global rank-ordered request
ordering, uniqueness, peer agreement, and output parity. This demonstrates the
control-plane ordering needed before multi-GPU serving; it does not establish
GPU inference, HTTP routing, network latency, or multi-host capacity.

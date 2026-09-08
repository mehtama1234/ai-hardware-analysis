# Sharded expert inference reference

Verified local result: all twenty-four rank/scenario comparisons passed across two
CPU/Gloo processes, with maximum absolute output error zero in these fixtures.
Capacity masks matched exactly and recorded source hashes were checked current.
See `reports/distributed-reference-cpu.json`. This experiment is now included in
the verified 97-test/fourteen-CPU-experiment advanced checkpoint.

Coordinated rejection is also verified: both ranks rejected mismatched capacity
and NaN input supplied only on rank one, reported matching reasons, passed a
barrier and then completed all normal cases. Thirteen MoE unit tests pass, including
three contract tests and ten mathematical-reference/learning-mechanism tests.
They are included in the expanded aggregate test total.

```bash
python3 gpu-mode-curriculum/moe-routing-all-to-all/run_distributed_reference.py
```

The runner starts two local CPU/Gloo processes. Each candidate invocation receives
its local token slice and only two of four expert weight matrices. The test fixture
retains global tensors separately to compute the single-process oracle.

The protocol is deliberately explicit:

1. Exchange local validation results and a small contract signature. Reject
   invalid input on any rank or mismatched expert dimensions, dtype, k or capacity
   on every rank before payload traffic. Then select unique top-k experts locally.
2. All-gather counts, then use rank-prefix counts to enforce one global capacity
   per expert. Rank order followed by local token order matches the reference's
   concatenated-token admission order.
3. Pack accepted token vectors by destination owner and local expert into padded
   buffers. Execute all-to-all; each owner receives source-ranked expert inputs.
4. Apply only locally owned linear expert weights. Execute a second all-to-all
   to return expert outputs to their source ranks.
5. Combine returned contributions using the source rank's original token indices
   and selected-logit gates. Dropped gates are not renormalized.

Cases cover ordinary logits without drops, skewed logits with global drops, tied
logits, zero capacity, a 1/5 token split and a 0/6 token split, each in FP32 and FP64.
Every rank checks output tensors
and the exact capacity mask against the tested CPU reference. The report retains
per-rank arrays, errors, versions and source hashes. Collective timeout is 30
seconds; the parent bounds joining at 90 seconds and cleans up its own children.

This is inference-only CPU execution, not distributed autograd or GPU evidence.
Padded buffers allocate capacity for every source/expert pair and compute unused
zero slots; the protocol is intentionally not bandwidth or compute efficient.
Zero capacity still exchanges counts but skips payload exchange. All ranks must
enter the same call. Contract negotiation uses Python object collectives only
among trusted local test processes; it is not a protocol for untrusted peers.
Process death or a rank that never enters the call still requires timeout handling.
No timing or overlap claim is
made. The runner and MoE tests passed in the expanded aggregate's isolated run.

The expanded runner also exercises a capacity mismatch and NaN input on only
rank one. Both ranks must reject each case and subsequently pass a barrier before
the normal output tests execute. This distinguishes coordinated rejection from
a timeout or unusable process group. Unit tests separately cover local contract
validation and mocked peer disagreement; they are not process execution evidence.

Next acceptance gates include more ranks,
variable-size payloads, expert MLPs and
GPU-backed execution. See [the mathematical reference](REFERENCE.md) for routing
semantics and scalar/gradient validation.

## Multi-GPU CUDA/NCCL promotion path

The end-to-end sharded GPU runner is now available separately from the single-
GPU routing smoke:

```bash
torchrun --standalone --nproc_per_node=2 \
  gpu-mode-curriculum/moe-routing-all-to-all/run_gpu_moe_multirank.py
```

Each rank owns two expert matrices, exchanges padded token payloads and expert
outputs with `all_to_all_single`, and compares its result and exact capacity
mask with the global CPU oracle. Seven timing samples are not claimed here;
the current runner records one bounded correctness execution plus elapsed
dispatch/compute/return time per rank. Hosts without CUDA or enough devices
write `reports/gpu-moe-multirank.json` with `unavailable:*` and never fall back
to Gloo. The current development host therefore has an explicit unavailable
preflight, while the multi-GPU acceptance gate remains open.

## Exercise: global capacity without gathering tokens

Two ranks offer `[2,1]` and `[3,2]` assignments to two experts, with capacity two.
Derive the accepted counts without moving token payloads. Then explain why a
rank with no source tokens must still participate in both payload exchanges.

Solution: rank zero has prefix `[0,0]` and accepts `[2,1]`. Rank one's prefix is
`[2,1]`; its remaining capacities are `[0,1]`, so it accepts `[0,1]`. Total accepted
counts are `[2,2]`. Using raw offered prefix counts is correct for first-arrival
admission: once earlier offered assignments exceed capacity, no later assignment
can be accepted. This assumes unique expert selection per token and the declared
rank/token order; it is not priority-by-gate admission.

A rank with no source tokens can still own experts receiving other ranks' tokens.
Skipping an exchange on that rank would violate the collective sequence and
omit that expert computation. Its receive buffer can be nonempty even though
its accepted-source mask and final output have zero rows. The `empty-source`
case exercises precisely this distinction.

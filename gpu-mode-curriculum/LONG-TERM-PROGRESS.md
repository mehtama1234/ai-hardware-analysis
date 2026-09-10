# Long-term program execution checkpoint

Started 2026-09-09 following explicit user instruction to execute the
[full program](LONG-TERM-END-TO-END-GOAL.md). The active goal label `start` refers
to that complete program, not merely the first milestone or the earlier closed
inference slice. Do not mark it complete until the full program audit passes.

## Current milestone: C — broader HTTP workloads, sustained arrivals, and replay

Latest: the three-way matched serving run `comparison-decode-20260909T192009`
passed 18 tests and raw-data validation across 18 arrival windows. All 4,608
requests reconcile: 2,256 correct completions, 2,352 rejections, zero failures.
Current experiment source hashes match; the T4 session stopped. The next gate
is dependency-closed source-bundle replay of this dynamic serving comparison.
See [matched results](analysis/matched-serving-decision.md).

Latest acceptance: `load-decode-20260909T190840` passed 15 tests, the previous
slot/HTTP proofs, and six mixed-length arrival windows. Of 1,088 offered
requests, 741 completed with reference outputs, 347 were rejected, and none
failed. Controlled HTTP EOS terminated after two tokens. The raw-data verifier
passes and current source hashes match the captured run; the T4 session stopped.

The next gates are a native microbatch comparison with identical arrivals and
budgets, exact-source replay of dynamic serving, and longer/broader workloads.
The generated [load decision](analysis/continuous-load-decision.md) records this
bounded operating envelope; it does not establish a baseline speedup or
production capacity.

Per-slot lifecycle and a bounded actual HTTP dynamic-admission proof now pass.
In `continuous-decode-20260909T185814`, the peer completed 32 reference tokens,
the canceled request emitted two correct tokens, and its slot was reused by a
replacement that completed 32 reference tokens while the peer remained active.
All six tests and both downloaded report verifiers pass; current source hashes
match. The session stopped after download. See the detailed continuation below.

Next: variable output budgets/EOS over HTTP, admission/overload controls under
sustained arrivals, matched baseline comparisons, and independent replay of the
dynamic engine. This bounded functional proof does not close the serving capstone.

## Prior milestone: per-slot cache lifecycle and dynamic admission

The bounded fixed-batch graph milestone below now passes matched profiling,
separate stage timing, pretrained token/logit checks, and exact-source replay
in a distinct T4 session. All 43 required dependency versions matched. Both
v0.2 sessions are stopped, their artifacts validate, and current experiment
sources match their captured hashes. The complete A–H program remains active.

The next implementation must replace the shared batch cursor with per-slot
positions/cursors and explicit ownership. Admission prepares a new request
without disturbing existing slots; EOS/completion/cancellation reclaims a slot;
reusing it must preserve peer outputs and erase prior request state. Validate
these contracts against individual library generation on CPU and GPU before
connecting the engine to the HTTP scheduler and sustained arrivals.

## Completed bounded milestone: A/B/C — fixed-batch decode and CUDA graphs

The first controlled comparison holds batching constant and compares:

1. Native dynamic-cache eager GPT-2 decoding.
2. Fixed-capacity cache with an explicit eager GPT-2 decode step.
3. The same fixed-capacity decode step captured in a CUDA graph.

Prefill remains in Transformers. Graph capture/setup is recorded separately.
Different prompt lengths reuse the same graph and cache allocations to test
reset/position correctness. CPU tests use a small random GPT-2 and check logits
as well as generated tokens; pretrained GPU results require the GPU runner.

New implementation:

- `batch1-decode-vertical-slice/graph_decode.py`
- `batch1-decode-vertical-slice/run_real_model_graph_decode.py`
- `batch1-decode-vertical-slice/tests/test_graph_decode.py`

CPU validation: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python3 -m pytest
gpu-mode-curriculum/batch1-decode-vertical-slice/tests/test_graph_decode.py -q`
passed two tests; the CUDA case is explicitly skipped (68.65 seconds). Tests
cover generated tokens, logits, long/short prompt reuse, stable allocations,
exhausted generation budgets, invalid padding, and capacity rejection.

The first GPU session `graph-decode-20260909T183016` completed and was stopped.
All three tests passed on T4, including actual graph replay. Its captured report
and traces are under `gpu-runs/imports/graph-decode-20260909T183016/reports/`.
`verify_graph_decode.py` passes, checking source/trace hashes, raw token outputs,
sample ordering, medians, coverage, and observed CUDA graph launches. Six
mutations of the real report (tokens, trace hash, launch evidence, median,
source hash, and order) were rejected by the validator.

First-session median complete generation time, milliseconds (16 output tokens;
five samples per mode; includes prefill/reset, excludes graph capture):

| Batch | Fixture | Dynamic eager | Static eager | Static graph |
| --- | --- | ---: | ---: | ---: |
| 1 | 0 | 139.72 | 129.87 | 52.76 |
| 1 | 1 | 231.00 | 212.67 | 59.36 |
| 1 | 2 | 163.14 | 166.43 | 55.62 |
| 4 | 0 | 190.44 | 171.39 | 83.88 |
| 4 | 1 | 250.29 | 221.58 | 80.14 |
| 4 | 2 | 199.74 | 165.82 | 88.44 |

All six fixtures pass pretrained output parity. This is a bounded first-session
result, not continuous serving or independently reproduced acceptance.

After this run, code inspection identified that switching to eager execution
could replace the public logits reference. The engine now retains and exposes
the captured logits allocation on graph replay. The CUDA test now switches
between eager and graph execution. The second fresh-session run,
`graph-decode-20260909T183338`, completed and was stopped. All three tests passed
(19.22 seconds), all six pretrained fixtures matched reference outputs, the
artifact verifier passed, and both captured implementation source hashes match
current code. The first run's source snapshot remains authoritative for its
results; the earlier local test artifact is historical and predates this correction.

Second-session median complete generation time, milliseconds:

| Batch | Fixture | Dynamic eager | Static eager | Static graph |
| --- | --- | ---: | ---: | ---: |
| 1 | 0 | 137.70 | 130.39 | 53.36 |
| 1 | 1 | 173.50 | 155.37 | 53.90 |
| 1 | 2 | 164.04 | 156.88 | 54.90 |
| 4 | 0 | 204.28 | 168.37 | 83.07 |
| 4 | 1 | 184.02 | 167.28 | 76.44 |
| 4 | 2 | 256.28 | 220.17 | 88.23 |

Graph replay improves all six fixtures in both sessions. Each separate profile
observes 15 graph launches for 15 decode steps. Runtime: T4, float32,
Transformers 5.12.1, PyTorch 2.11.0+cu128, Python 3.13.15; TF32 disabled.
This is a fresh-session repeat with a small output-reference correction, not
an exact source-bundle independent replay. Matched native/static/graph profiles,
separate prefill/decode measurements, and broader pretrained logit checks remain
open before advancing this milestone to full acceptance.

Handoff command: `bash gpu-mode-curriculum/scripts/run_graph_decode_colab.sh`.
The wrapper owns only the new named session and stops it after downloading
results; it does not reuse other sessions.

Next gates: per-slot admission/cache lifecycle → sustained HTTP load. CPU
numerical/reset tests, pretrained three-way GPU comparison, matched profiling,
and source-bundle replay now pass. The experiment remains fixed-batch and does not implement
continuous batching. See [run instructions](batch1-decode-vertical-slice/GRAPH-DECODE.md).

## Program ledger

| Package | Status | Remaining acceptance |
| --- | --- | --- |
| A Experimental foundation | In progress; existing evidence infrastructure reused | Shared contracts and independent capstone reproduction |
| B Kernels/compiler/layouts | In progress; graph decode step added | Full kernel/DSL/synthesis and hardware coverage |
| C Inference | In progress; prior bounded microbatch slice complete | Graph validation, token admission, reclamation, sustained HTTP load |
| D Training/precision | Open; earlier bounded lab evidence retained | Real-data multi-seed learning and training-to-serving comparison |
| E Distributed/placement | Open | Multi-GPU MoE/collectives and measured placement validation |
| F Multimodal/simulation | Open | Both application extensions and learning evidence |
| G Portability/hardware | Open | Executed second-stack and consumer/edge comparisons |
| H Research/teaching | Existing workbench foundation | Complete coverage, capstone paths, assessments, final audit |

Preserve the completed slice's immutable report/source bundles and unrelated
working-tree changes. New results must have distinct artifact identities.

## Matched profiling and exact-source replay continuation

The next experiment uses schema `real-model-graph-decode-v0.2`. It adds:

- Separate synchronized prefill/decode samples for every mode and fixture,
  collected separately from uninstrumented complete-generation timing.
- Matched compressed CPU/CUDA traces for all three modes on identical inputs.
- Pretrained logits compared at every decode step for static eager and graph.
- A checksummed source archive, source manifest, and recorded dependencies.
- An isolated replay runner checking the recursive torch/transformers dependency
  closure, source identity, runtime, workload, reference tokens, and the direction
  of the measured graph/eager comparison.

The archive test passes valid extraction and rejects source/dependency changes,
extra archive members, symlinks, and a bad archive checksum. The expanded GPU
run `graph-decode-20260909T184008` completed, passed v0.2 validation, and its
session stopped. The exact-source replay `graph-decode-20260909T184413` passed
and its session stopped. Previous v0.1 reports remain
historical evidence and are not silently promoted to these stronger gates.


The v0.2 original run validates logits for all 15 decode steps of both static
modes across six fixtures. Maximum absolute logit error across the recorded
checks is 0.001526; all pass the predeclared elementwise rule
`abs(error) <= 2e-4 + 2e-4 * abs(reference)`. This is not an absolute-only 2e-4
claim. Generated tokens match exactly.

Matched profiles show ordinary launch calls falling from 4,858 to 398 plus
15 graph launches for batch 1, and from 5,416 to 388 plus 15 graph launches for
batch 4. Static eager still issues 4,853/5,398 ordinary calls; moving to a static
cache alone does not remove per-operation dispatch. Graph execution still runs
GPU kernels. The report validator now cross-checks graph-launch summaries
against raw trace events as well as checking file hashes.

The generated [decision](analysis/graph-decode-decision.md) and
[underlying JSON](analysis/graph-decode-decision.json) retain complete timings,
separate stage medians, operator counts, logit errors, and provenance. Stage
samples have extra synchronization; dynamic prefill starts after initial cache
and position setup, whereas static prefill includes reset/validation. They must
not be added to or substituted for uninstrumented complete-generation latency.

## Exact-source replay accepted for the bounded graph experiment

`gpu-runs/imports/graph-decode-20260909T184413/reports/graph-reproduction.json`
passes with no errors. Local inspection checked its original/replayed report
hashes, 43 dependency version pairs, source identity, and current source hashes.
The replay's own v0.2 artifact verifier also passes, including raw trace checks.
Runtime, protocol, inputs, reference tokens, and model/tokenizer revisions match.

The declared reproducibility criterion is that graph median generation time
remains below both eager modes for every fixture, alongside correctness. It
passes; native/graph median ratios in the replay range from 2.38 to 3.87.
This reproduces the direction of the performance conclusion, not absolute
latency equality. Maximum recorded absolute logit error remains 0.001526 and
passes the recorded combined absolute/relative tolerance.

The generated decision now includes both v0.2 sessions. Four real-report
mutations (launch summary, logit status, stage time, archive hash) are rejected.
The source-archive integrity test also passes. No part of this result establishes
dynamic admission, reclaimed-slot correctness, HTTP graph serving, or sustained
capacity; those are the next gates.


## Per-slot lifecycle implementation and GPU evidence

`slot_decode.py` adds per-request cursor/position tensors, generation-tagged
ownership handles, synchronous admission prefill, independent output budgets,
EOS/completion reclamation, and explicit cancellation. Reclamation zeros the
slot's keys, values, mask, positions, input token, and exposed logits. Stale
handles cannot cancel a new owner. Inactive slots use cleared state during
fixed-shape graph replay. This preserves the earlier fixed-batch engine unchanged.

The local lifecycle test passed (one CPU pass, one CUDA skip; 48.98 seconds).
`slots-decode-20260909T185347` then passed all five CPU/CUDA graph and slot tests
on T4 (20.57 seconds), and both eager/graph pretrained lifecycle scenarios passed
all 12 checks. The artifact `reports/slot-lifecycle.json` and captured sources
validate with `verify_slot_system.py`. That session stopped after download.

The scenario keeps a peer active while canceling another request, verifies cache
clearing, reuses the canceled slot, rejects its stale handle, compares peer cache
before/after admission, and checks all outputs against individual library tokens.
It also covers completion, one-token admission, controlled EOS, idle ticks, and
empty cache after drain. Controlled EOS is not a claim about natural EOS rates.

`continuous_service.py` adds a single-worker token-boundary scheduler using the
existing HTTP transport. Admission work is bounded per tick to avoid starving
peers when immediate-completion requests keep arriving. The local scheduler test
passes and proves replacement admission before the peer completes.

The actual HTTP experiment `continuous-decode-20260909T185814` passed and stopped.
It demonstrates canceled-slot reuse with an active peer, correct streamed outputs,
client/server token accounting, and empty cache after drain. This is a bounded
three-request functional experiment; sustained arrival load, variable HTTP output
budgets, overload characterization, chunked prefill, and independent replay of
the dynamic engine remain open.

The final HTTP admission record is: peer → slot 0/generation 1; canceled request
→ slot 1/generation 1; replacement → slot 1/generation 2 with the peer still
active. Client token counts are 32, 2, and 32 respectively. Both reports in this
run pass `verify_slot_system.py`; its five implementation source hashes match
current files. Four mutations of the HTTP evidence (peer output, client/server
accounting, reuse generation, and active-peer admission) were rejected.

The [decision JSON](analysis/continuous-admission-decision.json) records the
report hash, checks, admission history, output counts, and open gates. See
[slot/HTTP run instructions](batch1-decode-vertical-slice/SLOT-DECODE.md).


## Mixed-length HTTP and repeated arrival-load continuation

`ContinuousScheduler.submit` now accepts a validated per-request output budget,
assigns it before enqueueing, and records `max_new_tokens` and `finish_reason`.
A separate `continuous_http.py` transport exposes this without changing the
historical fixed-budget HTTP transport. Scheduler checks reject output beyond
the budget and premature completion without EOS.

Ten local scheduler/HTTP tests pass (4.95 seconds): replacement admission,
1/3/6-token responses, early EOS, seven invalid budget forms, HTTP 429 when the
queue is full, and queued cancellation without model execution.

`run_continuous_load.py` is the next GPU experiment. Its predefined protocol uses
two slots, eight pending requests, budgets 1/8/16/32, offered rates 4/16/48 requests
per second, eight-second arrival windows, and two rounds with reversed rate order.
It retains all planned/actual arrivals, token arrival times, terminal records,
rejections, output reference checks, and allocator peaks. Goodput requires TTFT
<=1,000 ms, completion <=3,000 ms, and every inter-token gap <=500 ms; its time
window includes drain. Arrival lateness is measured rather than assuming the
load generator achieved the offered schedule. A separate controlled EOS probe
uses a known reference token as the configured EOS token.

The GPU handoff `load-decode-20260909T190840` completed and stopped. Fifteen
tests passed in 24.46 seconds, including CUDA graph/slot tests and HTTP budget,
EOS, invalid-input, rejection, and queued-cancellation tests. Both earlier
pretrained functional proofs also passed with the current scheduler.

The six arrival windows produced 741 correct completed requests, 347 HTTP 429
rejections, and zero failures. All raw client/server records reconcile. At 16
offered requests/s, both rounds completed all 128 requests with completion p95
174.44/176.64 ms. At 48 offered requests/s, the two rounds completed 224/197
and rejected 160/187; accepted goodput was 26.66/23.57 requests/s with completion
p95 476.62/545.58 ms. Load-generator arrival lateness p95 was below 1.90 ms in
every window. A separate controlled EOS probe completed after two tokens.

`verify_continuous_load.py` recomputes throughput, goodput, percentiles, schedule,
budgets, token correctness, finish reasons, and request accounting. Its first
run exposed a verifier schema mistake: streamed terminal events contain the
`type: done` envelope field while stored records do not. The corrected comparison
requires that envelope and exact equality of every remaining payload field; the
raw GPU report was unchanged. Validation now passes. Six mutations (tokens,
budget, goodput, arrival schedule, server record, EOS finish reason) are rejected.

The [generated decision](analysis/continuous-load-decision.md) and
[JSON evidence](analysis/continuous-load-decision.json) contain the report hash,
runtime, protocol, metrics, and limitations. Matched native microbatch comparisons
and exact-source dynamic-engine replay remain open. Eight-second arrival windows
do not establish long-duration or production capacity.


## Matched native/graph scheduling comparison in progress

`microbatch_control.py` adds a fixed-group scheduler and two controls. The native
backend batches prefill and compacts completed rows out of its dynamic cache;
requests retain their individual output limits. The graph control uses the same
slot engine as continuous serving but admits no new group until the current group
ends. Both microbatch controls use a five-millisecond grouping window. Stage
fields in these controls are placeholders, not measured stage timings; the
comparison uses actual client timing.

Local control tests passed (two CPU passes, one CUDA skip; 35.91 seconds),
including compaction with different prompt/output lengths against individual
library generation. The T4 experiment `comparison-decode-20260909T192009` is now
completed and stopped. Its protocol compares native microbatch, graph microbatch, and graph
continuous admission at 16/48 offered requests per second, eight-second windows,
three rounds, identical budgets/prompts/queue limits, and each mode occupying
every order position once per rate. Per-budget accepted counts expose selection
changes under overload.

All 18 CPU/CUDA tests passed in 23.25 seconds. The earlier lifecycle and HTTP
reuse probes also passed. `verify_serving_comparison.py` validates all 18 windows,
source hashes, matched arrival plans/budgets, per-request reference output,
client/server records, goodput, latency percentiles, budget mixes, and order.
Six mutations (order, budget, goodput, accepted mix, tokens, source hash) were
rejected. The generated [decision](analysis/matched-serving-decision.md) retains
[JSON summaries and paired rounds](analysis/matched-serving-decision.json).

At 16 offered requests/s, both graph policies completed all 384 requests across
three rounds. Median per-window completion p95 was 226.00 ms for graph groups
and 174.78 ms for continuous admission; median per-window TTFT p95 was
145.77 versus 25.34 ms. These are medians of window percentiles, not pooled p95.

At 48 offered requests/s, median goodput was 16.61 requests/s for graph groups
and 26.33 for continuous admission. The continuous/group goodput ratio was
1.45–1.63 across paired rounds. Their accepted output-budget mixes differ under
overload and remain visible in the JSON, along with token throughput. The native
control had materially lower goodput, partly because queued requests missed
the declared TTFT target; goodput ratios must not be called kernel speedups.

This closes the bounded matched-control experiment, not the full serving
capstone. Independent dynamic-serving replay, longer/broader workloads, a second
pretrained attention architecture, an established compatible serving-system
comparison, and further cache/prefill investigations remain open. Earlier
fixed-batch graph replay evidence does not close dynamic-serving reproduction.


## Dynamic-serving reproduction prepared; GPU capture pending

The comparison runner now emits a v0.2 source archive, manifest, and recorded
dependencies. `replay_serving_comparison.py` extracts verified sources into a
fresh directory, checks the dependency closure and runtime identity, executes
the captured workload, validates raw results, and checks the declared performance
directions. Existing comparison or reproduction outputs are rejected before
execution, preventing reuse of stale evidence. The Colab handoff supports this
replay through `SERVING_REPLAY_REPORT`.

The attempted capture `comparison-decode-20260909T192909` failed before session
creation with Colab `TooManyAssignmentsError` (HTTP 412). The session list showed
two T4 assignments with unrecognized names; neither was stopped. There is no
v0.2 GPU result or dynamic-serving reproduction result yet. The accepted v0.1
comparison remains authoritative; its evidence is not retroactively attributed
to the new source.

Local replay tests passed: three tests covering archive integrity/tampering,
both required performance directions, and rejection of stale output artifacts.
The next GPU step is a fresh v0.2 capture followed by an independent source-bundle
replay. This capacity gate does not close or block the complete A–H program;
training/backward and other CPU-verifiable work remain available.


## Training capstone: executable recomputed loss

The preceding turn made progress by preparing dynamic-serving replay and testing
its acceptance/integrity checks. With GPU allocation pending, package D now has
an executable token-chunked linear cross-entropy and analytical custom backward.
It saves input states, weights, labels, optional bias, and valid count, then
recomputes logits/softmax per chunk during backward. The mathematical derivation,
supported contract, and limitations are in
[fused-training-kernels/LINEAR-CROSS-ENTROPY.md](fused-training-kernels/LINEAR-CROSS-ENTROPY.md).

Five CPU tests passed in the initial run (8.290 seconds): finite-difference
derivatives across chunk sizes/reductions with noncontiguous inputs and bias;
ignored rows; large logits; saved-tensor inspection; and three-seed tied-weight
AdamW update/state parity over five steps each. The final rerun additionally
checks valid-label gradients with frozen weights and explicit autocast rejection.
The existing modeled timing scenarios were preserved as modeled evidence.

This implementation is PyTorch matrix operations with custom autograd, not a
fused device kernel. Synthetic optimizer parity does not close real-data learning.
Next work is pinned data/splits and matched fine-tuning integration, followed by
GPU memory/time measurements and checkpoint-to-serving evaluation. Float32/float64
are supported; native low precision and higher-order derivatives are not.


## Pinned real-data full-parameter training integration

The previous turn made progress through an executable custom backward and five
passing CPU tests. This turn prepared a checksum-verified, commit-pinned Tiny
Shakespeare corpus and separately tokenized 90/5/5 contiguous character ranges
with the pinned GPT-2 tokenizer. The manifest records 301,966 training, 18,066
validation, and 17,995 test tokens. The runner never loads test tokens.

`fused-training-kernels/run_real_training.py` now runs full-parameter pretrained
GPT-2 updates with standard versus recomputed cross-entropy, identical sampled
offsets and initialization, disabled dropout, and matched AdamW settings. It
records partial progress/failures, validation before/after, per-step time/token
counts, CUDA memory when applicable, and optional checkpoint/optimizer artifacts.

The bounded CPU smoke completed both arms (seed 7, one update, eight training
tokens). Standard/recomputed training losses were 6.8750309944/6.8750529289.
Validation started at 6.0997972488 and ended at 6.1081809998/6.1081790924. Both
validation losses increased; this is integration evidence, not improved learning.
Only sixteen fixed validation tokens were evaluated. The host was shared with
other heavy work, and first-step times cannot support a performance conclusion.

Raw report and checksum-matching source snapshots are retained in
`fused-training-kernels/reports/real-data-cpu-smoke-01/`. Both subprocess arms
completed and the process exited zero. Python compilation and diff whitespace
checks passed. Checkpoint saving was not requested for this smoke and remains
unverified. Full raw-report verification, real-data gradient/parameter parity,
larger validation, multi-seed learning, time-to-quality, GPU measurements, and
checkpoint-to-serving evaluation remain open. See
[fused-training-kernels/REAL-DATA-TRAINING.md](fused-training-kernels/REAL-DATA-TRAINING.md).


## Real-data gradient and optimizer parity execution

The previous turn made progress by preparing pinned data and completing both
full-parameter CPU smoke arms. `check_real_training_parity.py` now checks every
trainable tensor's gradient, parameter after one AdamW update, and both optimizer
moments against a separately executed reference with identical initialization
and real-data tokens. Per-element tolerances are predeclared; source snapshots
and per-tensor checks are retained. Temporary reference tensors reduce resident
model memory. Two failure-detection tests passed, covering one corrupted element
and shared nonfinite values. Python compilation and diff checks passed.

The measured run is in progress under exec session 36345, writing
`fused-training-kernels/reports/real-data-parity-cpu-01/real-training-parity.json`.
Re-poll that handle before restarting. No pass is claimed until terminal output
and all tensor checks have been inspected.

The reference arm completed and persisted all 148 gradient tensors and 148
updated-parameter/moment files temporarily. The recomputed model has loaded;
exec handle 36345 remains live. A separate full-split evaluation helper and
passing final-partial-block/token-coverage test were added. This helper is not
yet integrated into the measured v0.1 runner.


## Full validation integrated; existing parity run preserved

The previous turn made implementation progress and verified that parity exec
36345 was live. This turn re-polled the same handle and observed continued
execution with substantial swap use; it was not restarted. No parity conclusion
is available yet.

Training runner v0.2 now defaults to all 18,065 validation targets and records
per-block NLL sums/counts, token-weighted mean, perplexity, and context policy.
`--validation-tokens` explicitly selects a labeled prefix probe. Source snapshots
include the evaluator. Two tests passed (0.207 seconds), including unequal block
losses that reject unweighted averaging. Compilation passed. The v0.2 runner
has not yet been executed end to end; v0.1 measured evidence remains unchanged.

Future parity comparisons now bound arithmetic temporaries to 262,144 elements
per chunk instead of allocating several full embedding-sized tensors. This does
not alter the already loaded code in exec 36345; its captured source remains
authoritative for the current experiment.


## Real-data parity failed; numerical diagnosis started

The preceding turn made progress through full-validation integration and bounded
checker allocations. Exec 36345 has now exited with code 1. All 148 trainable
tensors were checked: 29 gradient tensors (117 elements), 56 updated-parameter
tensors (3,815 elements), and one first-moment tensor (two elements) failed the
predeclared bounds. Second moments passed. Maximum absolute gradient error was
0.00051266; maximum parameter error was 0.0000199303. The original report and
source snapshots are preserved. Loss agreement did not establish update parity.

No tolerances were relaxed. `diagnose_loss_numerics.py` now isolates the output
loss on real pretrained hidden states, comparing full and chunked native
autograd with full/chunked custom backward and chunked log-softmax autograd.
It freezes output weights to isolate the hidden-state gradient before rerunning
the full model. Exec 29878 is live; poll it before restarting. Larger custom-loss
training promotion remains gated on resolving this discrepancy.

The head-level diagnostic exited zero. Native chunked and custom chunked
projections both had maximum hidden-gradient error 1.6719103e-5 relative to
full native projection, with no hidden elements outside the original bound.
Full-projection custom backward differed by only 1.4901161e-8. Chunked native
and log-softmax autograd losses were 6.8750429153 versus full-native 6.8750309944;
custom chunked loss was 6.8750529289. These results localize a substantial part
of the discrepancy to projection chunking, with additional loss-rounding error
from explicit logsumexp subtraction. They do not resolve full-model parity.

A full-model native-chunked autograd control is now running in a fresh directory:
`fused-training-kernels/reports/real-data-native-chunk-control-cpu-01/`. It keeps
the original tolerances and uses the bounded checker allocation implementation.


## Stable forward loss and matched-chunk diagnostic preparation

The preceding turn made progress by completing the head-level numerical diagnosis
and launching the full-model native-chunking control. Exec 87585 is still live
and has not been restarted. Its captured source predates this turn's edits.

The loss forward now selects the negative target log-probability from
`log_softmax`, avoiding subtraction of large nearly equal logit/logsumexp values.
A new float32 common-offset regression checks this failure case. All six loss
tests passed in 27.773 seconds, and the test process exited zero. This fixes the
separately observed loss-rounding issue; it does not close real-data update parity.

The parity tool now supports `--reference-chunk-size`: zero preserves full native
projection; a positive value permits a same-chunk native reference to isolate
custom-autograd error from chunked projection rounding. The original tolerances
are unchanged. This new configuration has compiled but has not been executed.
Do not attribute the new forward or reference option to older measured reports.


## Training report verification

The native-chunk control exec 87585 remains live and was re-polled; no terminal
report is available yet. A standalone `verify_real_training.py` now validates
training report status, pinned corpus/tokenizer and split hashes, arm/seed/sample
coverage, finite step metrics, v0.2 token-weighted validation block accounting,
and captured source hashes. It remains compatible with the historical v0.1 smoke
report. The v0.1 smoke report passes this verifier with zero errors.

The verifier does not infer learning quality or GPU performance, and it does not
turn the earlier failed parity report into a pass.


## Stabilized backward normalization recheck

The previous turn added the full-model native-chunk control; exec 87585 remains
live after another authoritative poll, with no result yet. This turn changed the
custom backward probability path from `softmax` to `exp(log_softmax)`, matching the
stabilized forward normalization family. Existing loss tests were rerun (process
exec 70014; still live at last observation) and diff checks passed.

A fresh focused pretrained-state diagnostic is running as exec 63845 in
`fused-training-kernels/reports/loss-numerics-cpu-02/`. It has not produced rows
yet because model loading is still underway. Do not use the earlier diagnostic as
evidence for this change, and do not restart either live process solely because
an observation yielded no output.


## Training verifier tamper coverage

The previous turn added stabilized backward normalization and reran six loss tests.
Exec 87585 (native-chunk control) and exec 63845 (new loss diagnostic) were
authoritatively re-polled and remain live; the diagnostic has finished model
loading but has not emitted rows. The six-test process completed successfully.

Three verifier tests now pass in 1.272 seconds: the historical CPU smoke report
validates, manifest checksum drift and unmatched training offsets are rejected,
and a NaN step loss is rejected. The verifier is therefore usable for existing
v0.1 artifacts while the v0.2/full-validation report remains unmeasured.
No parity, quality, or performance claims have changed.

The stabilized diagnostic report now contains all five rows. Custom full
projection has loss error 4.77e-7 and hidden-gradient max error 3.73e-9. Custom
chunked projection has loss 6.8750429153 and hidden-gradient max error 1.67e-5,
matching native chunked and log-softmax-chunked paths exactly at reported
precision. This confirms the custom derivative is not the main source of the
full-model mismatch; chunked float32 projection/reduction is. The diagnostic
process has emitted its complete report but its exec handle should still be
polled for terminal status.


## Native-chunk control still memory-bound

The preceding turn completed the stabilized head-level diagnostic. This turn
authoritatively re-polled exec 87585 and found it still running after 11 minutes,
with no losses/checks persisted and approximately 1.35 GB RSS. It was not
restarted or stopped. The completed diagnostic exec 63845 has five rows in its
report; its handle has not yet returned a terminal marker.

No new performance or learning claim is made. The next evidence needed remains
the native-chunk full-model terminal report, followed by a same-chunk custom
comparison if required.


## Verified wait on full-model control

This continuation re-polled exec 87585 and confirmed its process is still live
(`check_real_training_parity.py --candidate native_chunked`), while its report
remains `running` with no persisted checks. It was not restarted. The completed
stabilized loss diagnostic remains the strongest current numerical evidence.

The verifier and loss/unit tests remain green; no parity or quality conclusion
has changed. If the control eventually reaches a terminal state, inspect its
report before updating the numerical contract.


## Conservative training decision artifact

The previous turn verified the native control remained live. This turn added
`fused-training-kernels/build_training_decision.py`, which first runs the raw
report verifier and only computes paired validation/step summaries from accepted
completed arms. It labels historical bounded CPU data `review` and refuses a
clean decision when verification errors exist; it does not select checkpoints or
claim time-to-quality. The historical smoke report verifies cleanly and produced
`fused-training-kernels/reports/real-data-cpu-smoke-01/training-decision.json`
with one paired seed and `review` status. Python compilation and diff checks pass.


## Packed-weight representation started

The native-chunk training control remains live (exec 87585) with no terminal
report. Independent package-D work added row-wise symmetric signed-int4 packing
in `quantization-memory-formats/quantization_memory_formats/packed_int4.py`.
It records storage bytes, handles zero rows and signed nibbles, rejects invalid
inputs, and exposes an explicit dequantize-then-GEMM reference. Three tests
passed after the host's import delay. This is storage/round-trip evidence only;
no native low-bit GPU or quality claim is made. Documentation is in
`quantization-memory-formats/PACKED-INT4.md`.


## Packed-int4 artifact validation

The previous turn added packed signed-int4 weights and three passing tests. This
turn revalidated Python compilation and diff whitespace checks. The packed artifact
remains a CPU storage/dequantized-reference result; native low-bit execution and
quality are still open.

Exec 87585 was re-polled and remains live after 16 minutes, now in an OS D-state
under memory pressure, with its report still `running` and no checks. It has not
been restarted. The next authoritative step is its terminal state or a separately
resourced rerun; no new parity claim is possible from the stalled report.


## Reconfirmed incomplete parity artifact

This continuation re-polled exec 87585 at 17 minutes. The process remains live
in OS D-state with about 1.07 GB RSS; its report remains `running`, with no
losses or checks. The artifact is retained solely as an incomplete control. No
restart, termination, or evidence promotion occurred. Packed-int4 and all prior
CPU correctness artifacts remain the available independent progress.


## Memory-bounded output-head parity path

Exec 87585 was re-polled at 17:50 and remains live in OS D-state; its report is
still `running` with no checks. Rather than add another full-model optimizer
allocation, `check_output_head_parity.py` starts a separate bounded path: it loads
pretrained GPT-2 once, detaches real hidden states, and compares standard versus
recomputed loss, hidden gradient, output-head gradient, and one output-head SGD
update. It records source hashes and fixed tolerances. Exec 40624 is live and
writing `fused-training-kernels/reports/output-head-parity-cpu-01/`; poll it before
any restart. This is real-model loss evidence, not full-model training parity.


## Output-head parity still loading

The output-head parity process (exec 40624) was re-polled; it remains live with
no report yet, and its process is still present. The full native-chunk control
(exec 87585) likewise remains live with an unchanged running report. Neither was
restarted. The next useful evidence is the bounded head result, which avoids the
full optimizer-state allocation causing the long disk wait.


## Quantized linear quality metrics

The previous turn re-polled the full parity control; it remains live and reportless.
This turn added `quantization_memory_formats/quality.py`, which computes packed
and float storage bytes/ratio plus max absolute error, RMSE, relative L2 error,
and cosine similarity for dequantized linear outputs. Five quantization tests
passed in 2.184 seconds, including zero-reference stability and finite metric
checks. Documentation now records the evidence boundary: calibrated weights,
representative activations, native low-bit execution, model quality, and serving
throughput remain open.


## Training processes remain pending

Both authoritative jobs were re-polled again. Full control exec 87585 remains
live after 22 minutes with its report still `running` and zero checks (RSS fell
to ~74 MiB while it waits). Output-head exec 40624 remains live after 3:34 with
no emitted report (~459 MiB RSS). Neither was restarted or stopped. The quantized
quality metrics and prior diagnostic evidence remain the latest completed progress.


## Parity jobs rechecked

Both jobs were authoritatively re-polled. Full control exec 87585 remains live
after 23 minutes with an unchanged `running` report and zero checks. Output-head
exec 40624 remains live after 4:40; it has loaded GPT-2 but has not emitted its
report. Neither was restarted. This is a verified wait, not evidence of parity.


## Real GPT-2 output-head parity passed

The bounded output-head process exec 40624 completed successfully. Using actual
pretrained GPT-2 hidden states and a real Tiny Shakespeare training slice, it
compared standard and recomputed loss, hidden-state gradients (6,144 elements),
all 38,597,376 output-head gradients, and one output-head SGD update. Every
check passed fixed tolerances: loss max error 1.1920929e-5, hidden-gradient max
error 1.6719103e-5, head-gradient max error 1.1062622e-4, and updated-head max
error 2.9802322e-8. The report includes source hashes and exits with status passed.

This closes a real-model loss/backward/output-head gate, not full-model optimizer
parity or learning quality. The full native-chunk control exec 87585 remains live
with its unchanged running report and zero checks; it remains excluded from
evidence.


## Full control remains stalled

The output-head gate is complete, but exec 87585 was re-polled at 25:31 and
remains live in D-state with its report still `running`, one standard loss, and
zero checks. It remains excluded from evidence. A fresh Colab session-list query
(exec 24171) also remains live without output, so no GPU capacity state was
assumed.


## Capacity and process state rechecked

Exec 87585 remains live after 27:06 with an unchanged running report and no
checks. Its RSS is ~1.29 GiB and it is excluded from evidence. The Colab query
finally returned one unrecognized T4 session (`gpu-t4-s-kkb-usw4a1-1lu6i5x59ajpp`);
it was left untouched. No new GPU allocation was attempted.


## Checkpoint artifact gate prepared

The full control remains live and reportless. To advance the training-to-serving
loop without inventing a checkpoint, `verify_checkpoint_artifacts.py` now checks
recorded model-file hashes, optimizer/RNG training-state loadability, and step
counts for runs produced with `--save-checkpoints`. It reports
`not_applicable` when no checkpoint was requested, as in the historical smoke.
Python compilation and diff checks pass; no checkpoint claim is made yet.


## Checkpoint verifier exercised

The checkpoint verifier invocation completed with `not_applicable`, zero
checkpoint runs, and zero errors for the historical smoke (no checkpoint was
requested). The output-head parity process has exited and its passed report was
recorded earlier. Only the full native-chunk control remains live; it continues
to have an unchanged running report with no checks.


## Replaced stalled full control with scoped GPT-2 parity

The prior full native-chunk process was owned by this work and remained in disk
wait for over 27 minutes with no checks. It was terminated; its partial report
(`one standard loss`, `zero checks`, `running`) remains preserved and is explicitly
marked incomplete. The output-head parity gate had already passed.

`check_real_training_parity.py` now supports `--scope head_and_last_block`,
freezing all other GPT-2 parameters while exercising the real model's final block
and tied output head. A fresh run exec 91962 is live with ~300–380 MiB RSS, far
below the stalled full optimizer run, writing
`fused-training-kernels/reports/real-data-scoped-parity-cpu-01/`. It is a scoped
correctness result, not a full-model parity substitute; poll its existing handle.


## Scoped parity executing after model load

The scoped GPT-2 run exec 91962 was re-polled. It has loaded all 148 model
shards and is executing the two scoped arms; its report is present but still
`running` with no losses/checks yet. RSS remains far below the terminated full
control. Partial output is not treated as evidence.


## Scoped parity still executing

Exec 91962 was re-polled; it remains live after 3:34 with its report `running`
and no checks persisted. RSS is ~1.51 GiB during the scoped optimizer arm, so
this host is still under memory pressure despite freezing earlier layers. No
partial result is treated as evidence.


## Scoped full-model control terminated as incomplete

Exec 91962 reloaded GPT-2 for its second arm, then entered OS D-state again
(~1.29 GiB RSS) with no new checks. It was terminated as an owned stalled run.
Its partial report remains `running`, with one standard loss and zero checks, and
is explicitly incomplete. The passed output-head parity report remains the only
real-GPT-2 backward/update gate. No full-model parity or learning claim is made.


## Terminated reports made explicit

The two owned runs terminated under memory/disk pressure but their JSON reports
still said `running`. Both artifacts now say `terminated_incomplete` and include
termination metadata: the full native-chunk report stopped before checks, and the
scoped report stopped during its second arm before checks. Python compilation and
diff checks pass. This prevents stale process state from being mistaken for
active or accepted evidence.

The verifier now handles malformed/non-dict protocol fields gracefully. Running it
against the terminated parity artifact returns a clean failed result rather than
a traceback. Four verifier tests passed in 0.252 seconds, including this malformed
protocol case.


## Clean handoff after stalled runs

A process audit confirms neither parity script is still running. The two terminated
reports are now explicitly `terminated_incomplete`; the real output-head parity
report remains passed. The active milestone moves to quantized packed-weight quality
integration, with multi-step real-data quality, GPU execution, dynamic serving
replay, and the remaining A–H packages still open.


## Clean local baseline

The post-stall audit completed all local package checks. The fused-training suite
passed 14 tests in 18.530 seconds (loss derivatives/stability, evaluation
coverage, report tamper checks, and optimizer comparison). The quantization suite
passed five tests in 2.769 seconds (packing, storage, linear parity, and quality
metrics). The historical real-data smoke report verifier passed with zero errors.
No training process remains live. GPU execution, full-model multi-step quality,
checkpoint serving, dynamic-serving replay, and remaining A–H gates remain open.


## v0.2 real-data runner probe completed

The updated v0.2 runner completed both standard and recomputed arms (seed 7, one
step, sequence 8, eight training tokens, 16 validation targets). The raw report
passes `verify_real_training.py` with zero errors, and the decision builder now
handles structured validation metrics. Initial validation mean NLL was 6.5434942245
for both arms; after training it was 6.5332005024 (standard) and 6.5331959724
(recomputed), a difference of -4.53e-6. Both used the same sampled training
offset and token-weighted validation blocks.

The standard CPU step took 72.06 seconds on this contended host; the recomputed
step timing is retained in the raw report but is not a performance claim. The
decision is `review`, not selected: one seed/step and 16 validation targets
cannot establish learning quality, time-to-quality, or GPU behavior. This closes
v0.2 evaluator/source/verifier integration, not the D acceptance gate.


## Checkpoint-to-serving integration smoke completed

The v0.2 checkpoint smoke completed both standard and recomputed arms with
`--save-checkpoints` (seed 7, one step, sequence 8, eight training tokens,
16 validation targets). The training report verifier passed with zero errors, and
`verify_checkpoint_artifacts.py` passed both checkpoint runs with zero errors.
Each model/optimizer checkpoint directory is 1,493,420,983 bytes and includes
recorded hashes plus loadable optimizer/RNG state.

Standard/recomputed step losses were 6.8750309944/6.8750429153 and after-update
validation mean NLL was 6.5332005024/6.5331959724. Step wall times were
20.18/55.64 seconds on the shared CPU host and are not a performance claim. The
decision artifact is `review`, not a selected checkpoint: one seed, one update,
and a 16-target validation probe cannot establish learning quality, time-to-target,
GPU behavior, or serving improvement. The next gate is checkpoint reload plus
serving parity, then larger multi-seed/full-validation experiments.


## Checkpoint reload smoke passed

The saved recomputed checkpoint was reloaded with local files and the pinned GPT-2
tokenizer. `run_checkpoint_reload.py` generated four greedy tokens with an explicit
attention mask, yielding `To be, or not to be, a member of`. The v2 report records
checkpoint file hashes, a deterministic aggregate hash, tokenizer/model revision,
input/output IDs, and training-state step count 1. The process exited zero after
25.85 seconds. This closes CPU checkpoint reload/generation smoke only; the model
has not yet been attached to the HTTP serving transport or GPU serving benchmark.


## First training-to-serving loop completed

The saved recomputed checkpoint was loaded into `SlotDecode`, attached to
`ContinuousScheduler` and `continuous_http`, and exercised through one loopback
HTTP request with a four-token budget. The served tokens exactly matched greedy
reference generation from the same checkpoint. All checks passed: token parity,
completed length terminal, zero active/queued requests after drain, and zeroed KV
cache after shutdown. The process exited zero in 18.22 seconds.

This is a CPU one-request integration smoke. It closes the basic checkpoint →
continuous HTTP → cache cleanup path, not GPU serving latency/capacity, multi-request
quality, or independent dynamic-serving replay.


## Checkpoint HTTP smoke mechanically verified

`verify_checkpoint_http_smoke.py` now validates the CPU checkpoint-to-serving
report: pinned model/tokenizer identity, checkpoint file hashes, exact served vs
reference tokens, declared length terminal, zero active/queued requests, and all
cache-cleanup checks. It passed the saved recomputed checkpoint report with zero
errors after hashing its checkpoint files. This verifier does not imply GPU
performance or multi-request capacity.


## Multi-seed real-data quality probe completed

The v0.2 runner completed two seeds (7 and 19), two updates per standard and
recomputed arm, sequence 16, and 64 validation targets. The raw report passes
its verifier with zero errors; the decision builder reports two paired seeds and
`review`. Both arms improved validation NLL from the common 5.213942 baseline:
seed 7 ended at 5.176449/5.176447 (standard/recomputed), and seed 19 ended at
5.180595/5.180594. The median recomputed-minus-standard validation delta was
-1.31e-6.

Median recomputed/standard step-time ratio was 1.252 on this shared CPU host;
this is not a performance conclusion. The run uses only four updates per arm
and 64 validation targets, so it does not establish time-to-quality, robust
learning, GPU behavior, or checkpoint selection. Next gates are full validation,
longer budget, GPU execution, and selected-checkpoint serving.


## GPU training capstone handoff prepared

The CUDA execution handoff is reproducible through
`scripts/run_training_colab.sh`. It provisions a fresh T4 Colab session, uploads
the pinned corpus and training/evaluation/verifier sources, runs the v0.2 runner
for seeds 7 and 19 with four updates, sequence length 64, and chunk size 16,
then verifies the report before archiving a report-sized result under
`gpu-runs/imports/<session>/`. The remote driver self-assembles the Python
package and data directory from flat uploads so the run does not depend on
upload-layer directory creation.

The handoff passes local Python compilation, shell syntax checking, and
`git diff --check`. No CUDA result exists yet: the previous allocation gate
failed before session creation with Colab `TooManyAssignmentsError` (HTTP 412),
so this is execution-ready infrastructure rather than accepted GPU evidence.


## First accepted CUDA real-data training capture

The prepared handoff completed on a Colab T4 as
`gpu-runs/imports/training-capstone-20260909T214326/`. The run used the pinned
GPT-2 revision and Tiny Shakespeare manifest, float32, batch 1, sequence length
64, chunk size 16, four updates, and seeds 7 and 19. It ran both the standard
and recomputed loss arms, synchronized CUDA step timing, and full validation on
18,065 targets. The imported report passes `verify_real_training.py` with zero
errors; the remote driver, data preparation, training runner, checkpoint
artifact check (not applicable because GPU checkpoint payloads are not archived),
and decision builder all returned zero.

Both seeds improved validation NLL: seed 7 ended at 4.7333521 (standard) and
4.7333525 (recomputed), while seed 19 ended at 4.5920145 and 4.5920149. The
median recomputed-minus-standard validation delta was 4.21e-7. Steady-state
standard/recomputed step times were approximately 0.071/0.088 seconds, with
about 2.51 GB peak CUDA allocation. These are measurements for this bounded
protocol, not a production throughput claim or time-to-quality result.

This closes the first real-data CUDA training gate. Longer training, checkpoint
selection/reload on GPU, and GPU training-to-serving evaluation remain open.


## Longer CUDA quality budget completed

The parameterized handoff completed a 16-update T4 run for seeds 7 and 19,
again with standard and recomputed arms, sequence length 64, chunk size 16,
and full 18,065-target validation. The imported report is
`gpu-runs/imports/training-capstone-20260909T215804/reports/gpu-run/real-training.json`
and passes `verify_real_training.py` with zero errors.

Validation NLL fell from the common 4.831816 baseline to 4.3163991/4.3164006
(standard/recomputed) for seed 7 and 4.2645321/4.2645363 for seed 19. The
median recomputed-minus-standard delta was 2.88e-6; the median steady-state
step-time ratio was 1.166. Peak CUDA allocation remained approximately 2.51 GB.
This establishes a repeatable bounded learning trend and loss-path parity on a
real GPU. It still does not select a checkpoint, establish time-to-quality, or
prove serving behavior from a trained GPU checkpoint.


## GPU checkpoint-to-serving chain passed

The next T4 run saved all four training checkpoints remotely, selected the seed
7 recomputed checkpoint, and exercised it through the actual continuous HTTP
transport on CUDA. The compact report is
`gpu-runs/imports/training-capstone-20260909T220327/reports/gpu-run/gpu-checkpoint-serving.json`.
The remote training verifier passed all four checkpoint runs and the serving
report passed every check: reference/served token parity, four-token length
terminal, zero active or queued requests, and fully cleared KV cache. The
served token sequence was `[11, 257, 582, 11]`; measured TTFT was 31.6 ms and
completion was 84.1 ms for this one-request loopback.

This closes the first end-to-end training → selected checkpoint → CUDA serving
chain. It is a correctness and lifecycle gate, not a capacity or throughput
claim. Multi-request load, checkpoint selection across seeds, dynamic serving
replay, and the broader A–H program remain open.


## Multi-request CUDA load from the trained checkpoint passed

The same selected seed-7 recomputed checkpoint then ran the existing mixed-length
arrival harness for two reversed-order rounds at 4, 16, and 48 offered requests
per second, four seconds per window, with budgets 1/8/16/32 and two slots. The
imported report is
`gpu-runs/imports/training-capstone-20260909T221639/reports/gpu-run/checkpoint-load/continuous-load.json`;
both the remote and local `verify_continuous_load.py` checks passed.

All 16-request-per-second windows completed 64/64 requests with completion p95
178.2–186.1 ms. At 48 offered requests per second, 112/192 and 113/192
requests completed, 80 and 79 were explicitly rejected by the bounded queue,
and no request failed. Goodput was 25.48 and 25.79 requests/sec, with
completion p95 509.1 and 504.5 ms. Every window passed output parity,
accounting, drain, and KV-cache clearing; the controlled EOS probe also passed.

This is measured capacity behavior for one trained checkpoint and one slot
engine. It is not a claim of superiority because there is no matched native
microbatch baseline in this run. The next serving gate is a counterbalanced
comparison plus dependency-closed independent replay.


## Counterbalanced trained-checkpoint serving comparison passed

The selected seed-7 recomputed checkpoint was evaluated with the existing
three-way comparison harness: native microbatch, graph microbatch, and graph
continuous. Each mode occupied every order position once at rates 16 and 48,
for three rounds and four seconds per window. The imported report is
`gpu-runs/imports/training-capstone-20260909T222606/reports/gpu-run/checkpoint-comparison/serving-comparison.json`;
`verify_serving_comparison.py` passed all 18 runs with zero errors.

At 48 offered requests/sec, median goodput was 5.28 requests/sec for native
microbatch, 17.34 for graph microbatch, and 25.33 for graph continuous. At 16
offered requests/sec, median completion p95 was 1,231.2 ms, 208.3 ms, and
179.6 ms respectively. All modes preserved token parity and scheduler
accounting; overload rejection was explicit. The report includes the
dependency-closed source bundle and recorded requirements for later replay.

This closes the matched comparison gate for the trained checkpoint. The result
is protocol-specific and includes different prefill/control implementations;
independent source-bundle replay and broader model/workload characterization
remain open.


## Independent trained-checkpoint replay passed

The comparison source bundle was replayed in a fresh temporary directory with
`PYTHONPATH` cleared and the selected seed-7 recomputed checkpoint supplied
explicitly. The replay report is
`gpu-runs/imports/training-capstone-20260909T223403/reports/gpu-run/checkpoint-replay/serving-reproduction.json`.
All recorded dependencies matched the remote environment, the isolated replay
returned zero, and the replay verifier accepted all 18 runs. Both conclusions
reproduced: continuous median goodput exceeded native and graph microbatch at
48 requests/sec, and continuous median completion p95 was below graph
microbatch at 16 requests/sec.

This closes the dependency-closed dynamic serving replay gate for the trained
checkpoint. The remaining serving work is broader model/workload coverage,
chunked prefill and cache-policy experiments, and production-style capacity
characterization.


## Second pretrained model serving characterization passed

The arrival harness was generalized to accept a pinned model ID and revision,
then run on `distilbert/distilgpt2` revision
`2290a62682d06624634c1f46a6ad5be0f47f38aa` on a fresh T4. The imported report
is `gpu-runs/imports/alternate-model-20260909T224534/reports/alternate-load/continuous-load.json`;
the model-aware verifier passed with zero errors.

All 16-request-per-second windows completed 64/64 requests with median
completion p95 86.9 ms. At 48 offered requests/sec, the two rounds completed
177 and 151 requests, explicitly rejected 15 and 41, failed none, and achieved
median goodput 38.71 requests/sec. Output parity, controlled EOS, scheduler
drain, KV-cache clearing, and overload accounting all passed.

This establishes that the serving contract generalizes beyond the original
GPT-2 checkpoint while preserving the same bounded protocol. It is not an
architecturally different decoder family—DistilGPT2 retains GPT-2-compatible
blocks—so a genuinely different architecture remains a later research gate.


## GPT-NeoX architecture characterization passed

After diagnosing the initial batch-4 cached-versus-uncached divergence, the
Pythia-70M (GPT-NeoX) path was promoted against the authoritative Transformers
`generate` output. The final T4 report is
`gpu-runs/imports/architecture-characterization-20260909T230410/reports/pythia-serving-characterization.json`
and passes the model-aware verifier for batch sizes 1, 2, and 4. Cached
generation matches the framework reference at every batch size; the report
retains the uncached batch-4 mismatch as a numerical diagnostic rather than
silently discarding it.

Pythia uses 70,426,624 parameters. Cached/uncached median wall times for batch
4 were 48.7/45.0 ms, with allocator peaks 148.5/156.9 MiB. The protocol uses
homogeneous prompt replication per batch and eight greedy tokens, so this is a
cache and architecture characterization, not a full dynamic-slot serving
comparison yet. The genuinely different architecture gate is closed; adapting
GPT-NeoX into the slot engine and measuring longer mixed arrivals remain open.


## GPT-NeoX dynamic slot adapter and load passed

`HFSlotDecode` now provides an architecture-generic slot engine using model-native
Hugging Face caches, explicit position/cache positions, per-slot ownership,
cancel, EOS, and cleanup. The Pythia-70M adapter ran the same two-round,
4/16/48-request-per-second arrival protocol on a fresh T4. The imported report
is `gpu-runs/imports/architecture-characterization-20260909T230939/reports/pythia-load/continuous-load.json`;
the model-aware load verifier passed all six windows with zero errors.

At 4 req/s, both windows completed 16/16. At 16 req/s, both completed 52/64
and explicitly rejected 12; at 48 req/s, they completed 52 and 55, rejected
140 and 137, and failed none. Median completion p95 was 1,108.0 ms at 16 and
1,366.3 ms at 48, with median goodput 10.80 and 9.36 requests/sec. Output
parity, EOS, queue accounting, drain, and KV-cache clearing passed throughout.

This closes the first genuinely cross-architecture dynamic serving gate. The
generic per-slot path is correctness-first and slower than the GPT2-specific
engine; optimization, matched cross-architecture controls, and longer workload
characterization remain open.


## GPT-NeoX native-vs-generic comparison passed

The Pythia-70M adapter was then run through the same three-mode, counterbalanced
serving comparison harness: native microbatch, graph microbatch, and graph
continuous. The imported report is
`gpu-runs/imports/architecture-characterization-20260909T231914/reports/pythia-comparison/serving-comparison.json`;
the model-aware verifier passed all 18 runs with zero errors. The protocol
requires correctness and records per-mode metrics, but makes no assumption that
the generic engine must outperform the native implementation.

At 16 offered requests/sec, median goodput was 13.33, 9.96, and 10.60
requests/sec for native, graph microbatch, and graph continuous respectively;
median completion p95 was 662.6, 960.7, and 1,192.8 ms. At 48 offered
requests/sec, median goodput was 13.19, 5.80, and 8.08, with completion p95 of
868.9, 1,539.7, and 1,495.6 ms. All modes preserved output parity, queue
accounting, overload rejection, drain, and cache cleanup. The result closes the
cross-architecture comparison correctness gate and makes the optimization target
concrete: the generic path is currently slower on this workload.


## Generic GPT-NeoX decode allocation optimization implemented

The `HFSlotDecode` hot loop now owns a fixed attention-mask buffer per admitted
request and reuses the slot's token tensor for each decode step. This removes the
per-tick `torch.cat` mask growth and token-tensor allocation while retaining
explicit position IDs, cache positions, model-native KV state, cancellation, and
slot cleanup. The implementation is in
`batch1-decode-vertical-slice/hf_slot_decode.py`.

The new reusable-buffer generation/reclamation test and the existing slot tests
pass on CPU (`2 passed, 2 skipped` for CUDA-marked variants); the CUDA performance
effect is intentionally unclaimed until the same matched T4 comparison is rerun.
The next gate is a fresh counterbalanced Pythia comparison with this source,
followed by longer workload windows if the optimization improves the measured
operating envelope.


## Reusable-buffer optimization measured promising on T4

A fresh counterbalanced Pythia comparison using the reusable-buffer source
completed on T4 and passed verification for all 18 runs. The report is
`gpu-runs/imports/pythia-hf-buffer-opt-20260910T000000/reports/pythia-comparison/serving-comparison.json`.
For graph-continuous mode at 48 offered requests/sec, median goodput increased
from 8.08 to 10.83 requests/sec and median completion p95 decreased from
1,495.6 to 1,217.3 ms relative to the prior Pythia comparison. Output parity,
admission accounting, overload rejection, drain, and cache cleanup remained
valid.

The required repeat completed on a second fresh T4 at
`gpu-runs/imports/pythia-hf-buffer-opt-20260910T001500/reports/pythia-comparison/serving-comparison.json`
and also passed all 18 correctness checks. Its graph-continuous result at 48
req/s was 4.26 requests/sec and 1,869.2 ms p95. Across the two optimized runs,
the median was 7.55 requests/sec and 1,543.2 ms p95, so the earlier apparent
improvement is erased by run-to-run variance and is not promoted as a speedup.
The next work is profiler-backed attribution of allocation and launch behavior,
followed by longer repeated windows with a declared variance analysis.


## GPT-NeoX profile attribution passed

The corrected profile-only handoff now propagates its profile flag through the
uploaded manifest. The T4 report is
`gpu-runs/imports/pythia-profile-20260910T010000/reports/pythia-load/continuous-load.json`;
the load verifier passed all six windows with zero errors. It records synchronized
CUDA model timing, host-side preparation timing, tick counts, and active-slot
occupancy for every window.

Across the six windows, reusable-mask/token preparation cost 0.34–0.59 ms per
tick, while synchronized model execution cost 6.6–13.3 ms per tick. This makes
the current diagnosis concrete: the large run-to-run variation is dominated by
model execution and scheduling behavior, so the eliminated mask allocation is
not sufficient to explain or resolve it. The next instrumentation target is
worker admission and launch-gap timing, followed by longer repeated windows.


## Worker timing attribution narrows the bottleneck

The follow-up profiled run adds scheduler counters to the model timings. Its
report is
`gpu-runs/imports/pythia-profile-20260910T020000/reports/pythia-load/continuous-load.json`;
the verifier passed all six windows. At high offered rates, inter-tick host gaps
totaled 0.4–0.46 seconds over roughly 325–376 ticks, while admission took
6.9–9.1 ms per request. Synchronized model execution took 10.8–13.3 ms per
tick; preparation remained only 0.33–0.63 ms per tick.

The current diagnosis is therefore model-call and launch behavior, rather than
mask allocation or scheduler gaps, as the main source of throughput variance.
The next engineering experiment should compare batched model calls and CUDA
Graph launch behavior under the same slot mix, then repeat with longer windows.


## Longer profiled windows confirm model-call variance

The workload handoff now accepts an explicit duration, and a 12-second profiled
Pythia run completed on T4. The report is
`gpu-runs/imports/pythia-profile-20260910T030000/reports/pythia-load/continuous-load.json`;
all six windows passed verification. At 48 offered requests/sec,
graph-continuous goodput was 7.22 and 9.32 requests/sec across reversed rounds,
with 12.57–12.70 ms synchronized model time per tick. At 16 req/s, goodput was
10.21 and 6.99, with 11.66–13.33 ms model time per tick.

The longer windows did not make host gaps the dominant signal. Variance remains
inside model-call and launch behavior, so the next controlled experiment is a
batched-call versus CUDA-Graph launch comparison under the same slot mix.


## Profiled native-versus-generic comparison passed

The comparison harness now carries per-mode profile counters. The Pythia report
is
`gpu-runs/imports/pythia-comparison-profile-20260910T040000/reports/pythia-comparison/serving-comparison.json`;
the model-aware verifier passed all 18 runs. The report explicitly records that
HF generic modes use eager per-slot model calls, so their graph names refer to
scheduler controls rather than CUDA Graph captures.

At 48 offered requests/sec, graph-microbatch had median model time 9.53 ms/tick,
goodput 5.67 requests/sec, and completion p95 1,532.4 ms. Graph-continuous had
11.20 ms/tick, but goodput 10.53 requests/sec and p95 1,231.7 ms. This is a
useful systems tradeoff: fixed-group execution reduces per-tick model time, while
continuous admission converts more completed work into useful throughput.
The native backend profile is recorded in the follow-up artifact below; this
report's generic counters alone are not a launch-overhead conclusion.


## Native batched execution attribution passed

The native backend now records its own model-call counters in the same report.
The fresh Pythia artifact is
`gpu-runs/imports/pythia-native-profile-20260910T050000/reports/pythia-comparison/serving-comparison.json`;
the verifier passed all 18 runs. At 48 offered requests/sec, native batching
had median goodput 12.80 requests/sec, completion p95 981.7 ms, 6.19 ms
synchronized CUDA time per call, and an average batch size of 1.28. Preparation
was 0.07 ms per call. The generic controls measured 8.82 ms/tick for fixed
groups and 11.72 ms/tick for continuous admission.

This closes the first direct native-versus-generic execution attribution gate.
Native batching has the lower model-call cost and tail latency; continuous
admission still produces more useful throughput than fixed groups by admitting
new work at token boundaries. The next systems milestone is a true fixed-shape
batched generic cache path or CUDA Graph capture where the architecture permits
it, with correctness and cache lifecycle held constant.


## Fixed-capacity StaticCache comparison passed

`NativeBatchBackend` now supports a separate `StaticCache` mode with fixed
maximum cache length and explicit row compaction. The Pythia T4 comparison is
`gpu-runs/imports/pythia-static-cache-20260910T060000/reports/pythia-comparison/serving-comparison.json`;
the verifier passed all 18 runs. At 48 offered requests/sec, native static-cache
batching achieved median goodput 12.61 requests/sec and completion p95 983.9 ms,
with 6.56 ms synchronized CUDA time per call and average batch size 1.23. The
generic continuous control reached 9.41 requests/sec in the same comparison.

This closes the fixed-capacity batched-cache correctness gate. The implementation
is not claimed as CUDA Graph capture yet; the next experiment must test
architecture-compatible capture and report capture memory and launch cost.


## Pythia StaticCache CUDA Graph probe passed

The fixed-shape capture probe now passes on a fresh T4. The report is
`gpu-runs/imports/pythia-static-graph-probe-20260910T083000/reports/static-cache-graph.json`;
the standalone `verify_static_cache_graph_probe.py` also passes. It captures
eight decode steps for batch 2 with prompt width 5 and StaticCache capacity 17,
using SDPA masking. Graph replay has exact eager token parity and stable output
shape; allocator peak after capture was 173,031,424 bytes.

The earlier eager-attention attempt failed because GPT-NeoX eager masking creates
a CPU scalar during capture. That is now a concrete backend limitation, while
SDPA demonstrates architecture-compatible capture is feasible. The next gate is
integrating this capture into a bounded serving bucket with measured launch and
memory tradeoffs; dynamic admission and slot reuse remain open.


## StaticCache graph reuse exposes lifecycle boundary

An attempted second fixed-shape bucket using the same captured graph after
`StaticCache.reset()` and a new prefill failed the slot-reuse parity check. The
initial replay remained exact, but the reused graph diverged on the second
sequence. The failed diagnostic report is
`gpu-runs/imports/pythia-static-graph-reuse-20260910T093000/reports/static-cache-graph.json`.

This is a concrete serving limitation: fixed-shape capture is viable for one
cache lifetime, while safe graph reuse across reset and reprefill still needs a
graph-safe cache lifecycle or recapture policy. The standalone verifier treats
reuse as an optional check so the original capture gate remains independently
valid and the failed lifecycle evidence stays visible.


## Recapture-per-bucket restores StaticCache graph parity

The follow-up probe tested the safe lifecycle policy: reset and prefill a new
fixed-shape bucket, then recapture a graph before replay. The T4 report is
`gpu-runs/imports/pythia-static-graph-recapture-20260910T103000/reports/static-cache-graph.json`;
`verify_static_cache_graph_probe.py` passed both initial and slot-reuse parity.
Recapture took 8.47 ms, with allocator peak 174,660,608 bytes, and the second
bucket matched eager tokens exactly.

This establishes recapture-per-bucket as the currently safe graph lifecycle.
The earlier same-graph reuse failure remains a valid limitation, so serving
integration must account for capture latency and memory rather than assuming a
captured graph can survive arbitrary cache resets.


## Recapture-per-bucket bounded serving probe passed

The proven lifecycle is now exercised by a reusable `StaticGraphBucket` runner.
Two successive batch-2, prompt-width-5 Pythia buckets each reset and prefilled a
StaticCache, recaptured an SDPA CUDA Graph, and matched eager tokens exactly.
The T4 report is
`gpu-runs/imports/pythia-static-bucket-20260910T110000/reports/static-graph-bucket.json`;
`verify_static_graph_bucket.py` passes. Recapture took 13.78 ms for the first
bucket and 9.16 ms for the second; peak allocation was 182,135,808 bytes.

This closes the bounded fixed-shape bucket lifecycle gate. It is not yet an HTTP
dynamic-admission or amortized-capacity result. The next integration must put
bucket admission behind the scheduler and measure when recapture cost is paid
back by the bucket's served tokens.


## StaticGraphBucket HTTP integration passed

The recapture-per-bucket backend is now behind the existing HTTP scheduler. A
fresh T4 run served two successive buckets of two requests each, streamed eight
tokens per request, matched eager references for both rounds, and drained the
scheduler cleanly. The report is
`gpu-runs/imports/pythia-static-http-bucket-20260910T120000/reports/static-graph-http.json`;
`verify_static_graph_http.py` passes. Recapture took 15.00 ms and 8.66 ms for
the two buckets, with peak allocation 191,903,744 bytes.

This closes the bounded HTTP integration gate. The service still requires fixed
batch, prompt shape, and output budget; dynamic shape-bucket admission, mixed
arrivals, and amortized capacity remain the next serving experiments.


## Dynamic shape-bucket HTTP routing passed

The HTTP integration now routes requests by tokenized prompt width and output
budget into independent fixed-shape schedulers. A fresh T4 run sent four
concurrent requests spanning width-5 and width-6 classes; both buckets recaptured
their StaticCache graphs, streamed eight tokens, matched eager references, and
drained cleanly. The report is
`gpu-runs/imports/pythia-shape-router-20260910T160000/reports/static-graph-http.json`;
`verify_static_graph_http.py` passes. Recapture costs were 10.28 ms and 7.37 ms.

GPU ownership is serialized across concurrent bucket captures, while tokenization
is protected from concurrent borrowing. This closes the mixed-prompt-shape
routing gate. Mixed output budgets, bounded backpressure, and amortized capacity
under sustained arrivals remain open.


## Mixed-budget and backpressure experiment is implementation-ready

The next serving runner now routes two prompt-width classes across two output
budgets (4 and 8 tokens), keeps each CUDA Graph bucket fixed, and records exact
per-budget token references. Each bucket has a pending bound of two. A separate
12-request overload targets one bucket so HTTP 429 responses and scheduler
drain are measured explicitly. If a grouping window drains to a singleton, the
backend pads the graph input with a duplicate request and emits events only for
the real request; this preserves the fixed graph batch shape without turning
queue pressure into a model error.

Local compilation and the HTTP/static-cache regression tests pass (10 tests).
The first corrected T4 handoff was rejected by Colab assignment quota before
session creation at
`gpu-runs/imports/pythia-mixed-budget-backpressure-20260910T183000`. The same
bundle then completed on an A100 at
`gpu-runs/imports/pythia-mixed-budget-backpressure-20260910T190000`.
`verify_static_graph_http.py` passed: all eight primary requests matched exact
references, four shape/budget buckets recaptured, and the scheduler drained.
The 12-request overload produced four HTTP 200 responses and eight HTTP 429
responses. Recapture totaled 46.824 ms for 48 primary tokens, or 0.976 ms per
served token and 5.853 ms per primary request; peak allocation was 268,616,192
bytes. These are A100 measurements and are not compared numerically with the
earlier T4 results.

The exact rerunnable command is:

```bash
ARCHITECTURE_MODE=http-bucket \\
COLAB_GPU=T4 \\
COLAB_SESSION_NAME=pythia-mixed-budget-backpressure-<timestamp> \\
bash scripts/run_architecture_colab.sh
```

`COLAB_GPU` is configurable for an equivalent CUDA-capable accelerator when
the T4 pool is unavailable; the report always records the actual device.

The next authoritative gate is a comparable T4 run or a sustained mixed-arrival
workload, followed by integrating the measured backpressure policy into the
serving capstone.


## Sustained mixed-budget arrivals passed on A100

The runner now supports repeated primary rounds. Three rounds served 144
primary tokens across the four fixed shape/budget buckets, with exact token
parity, clean scheduler drain, and the same bounded overload result (4 accepted
and 8 HTTP 429 responses from 12 overload requests). The report is
`gpu-runs/imports/pythia-mixed-budget-sustained-20260910T200000/reports/static-graph-http.json`;
the standalone verifier passed.

Recapture totaled 102.986 ms, or 0.715 ms per primary token and 4.291 ms per
primary request. The one-round result was 0.976 ms per token, so repeated
rounds provide measurable amortization. The run used an A100 and loopback HTTP;
these figures are not interchangeable with earlier T4 measurements and do not
claim production capacity. A T4 allocation remains the next hardware
comparability gate before the serving capstone decision.


## Fixed-group cancellation correctness regression passed

The microbatch scheduler had a lifecycle edge case: if a request was canceled
after receiving a token, its backend could still emit a late row in the same
fixed group. The scheduler then looked up an already-completed request and
raised a false `KeyError`, potentially failing its peer. It now discards late
rows for requests no longer live while continuing to process the peer.

`test_microbatch_cancellation_discards_late_group_row` exercises this exact
interleaving and verifies the canceled request receives its partial token list,
the peer reaches its declared length, and the scheduler drains. The serving
HTTP/scheduler regression set passes 11 tests. This is local controlled-backend
evidence; CUDA HTTP cancellation and mixed cancellation under graph buckets
remain an open GPU gate.


## CUDA graph HTTP cancellation passed on A100

The cancellation race is now exercised through the actual streaming endpoint
and StaticCache graph backend. The probe report is
`gpu-runs/imports/pythia-static-graph-http-cancel-20260910T210000/reports/static-graph-http.json`;
`verify_static_graph_http.py` passed. The client received one token, sent a
second HTTP `/cancel` request, received `cancelled_inflight`, and the scheduler
drained. Mixed-budget parity, bounded 429 backpressure, and shape-bucket
recapture checks stayed green in the same run.

This closes the graph-bucket cancellation gate on an NVIDIA A100-SXM4-40GB.
The target T4 comparison and longer production-like cancellation streams remain
open; the run is loopback evidence rather than a production capacity claim.

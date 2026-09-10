# Real-model inference optimization loop

Status: **six bounded vertical-slice gates verified, 2026-09-09**.
The [audit](../analysis/real-model-goal-audit.json) passes all six gates;
20 local tests and the workbench verifier pass. The full advanced curriculum
remains a separate, broader goal.

Build one reproducible path from a real pretrained model to a measured serving
decision, then expose it through the GPU curriculum and workbench. This is the
active vertical slice of the [advanced goal](../advanced-lab-phase/END-TO-END-GOAL.md),
not a replacement for its broader training, distributed, and portability goals.

## Completion gates

1. **Trusted model baseline.** Pin GPT-2 and tokenizer identity, preserve prompt
   fixtures, match library generation, and prove that padding/batching preserves
   each request's output. Record the actual attention backend and numerical mode.
2. **Fair candidate comparison.** Compare native and custom kernels with identical
   inputs, batching, and token counts. Preserve synchronized raw samples,
   warmups, source hashes, runtime, memory, and all correctness checks. A failed
   correctness check must fail the experiment even if the candidate is faster.
3. **Bottleneck explanation.** Capture native and candidate profiler evidence and
   separate attention, projections, cache movement, allocation, and host overhead.
   Explain end-to-end changes using those measurements.
4. **Application boundary.** Exercise the selected correct path through a real
   model-serving endpoint with bounded arrival load, admission, cancellation,
   and request isolation. Report prefill/decode, TTFT, completion latency, tail
   latency, throughput, and memory with request accounting and output checks.
5. **Reproduction and decision.** Retain a rerunnable source/environment/input
   bundle and verifier. Publish whether the candidate helps, loses, or lacks
   evidence, with the exact baseline and workload. A measured loss is valid;
   silently narrowing the baseline to make a speedup is not.
6. **Teaching and workbench integration.** Connect the result to its mathematical
   reference, GPUMODE lessons, relevant papers, runnable commands, profiling
   explanation, and next experiment. Regenerate and validate the relevant pages
   and workbench measurement links.

The adjacent analog/hybrid decision package can consume this evidence. GPU
results alone do not establish analog performance or physical hardware benefit.

## Recovery implementation, 2026-09-09

- Corrected GPT-2 position IDs for left-padded cached decoding; offline tests
  compare both eager and SDPA against library and individual generation.
- Corrected explicit eager/SDPA selection, pinned model revision, alternating
  timing order, raw token capture, provenance, and failure exit status.
- Arrival comparison now checks individual/batched output parity, all three
  custom variants, repeat stability, and equally scheduled latency ratios.
- Added `verify_real_model_comparison.py` for captured v0.2 reports. Historical
  v0.1 reports remain unchanged and cannot satisfy these corrected gates.
- Fresh GPU run: `colab-real-model-sdpa-corrected-gpt2-20260909`; consult its
  downloaded v0.2 report passes the verifier and both captured source hashes
  match current code. Exact backend and batching parity pass; medians are
  671.62 ms eager and 664.39 ms SDPA, with five samples. This small difference
  does not establish a reliable speed advantage. All nine local slice tests pass.

## Measured continuation, 2026-09-09

- `colab-real-model-profile-corrected-gpt2-20260909` captures all four variants
  against library generation, with separate raw CUDA traces and timing samples.
  All outputs match. Paged wrappers issue 1,488 `nonzero` calls and 1,520 stream
  synchronizations, compared with 32 synchronizations in eager generation.
- `colab-real-model-profile-offsets-gpt2-20260909` verifies the vectorized
  mask-offset change: zero `nonzero` calls, 32 synchronizations, and exact parity.
  Paged remains slower than eager: 558.76 ms versus 383.35 ms median. This is a
  diagnosed and reduced overhead, not an accepted custom-kernel performance win.
- `colab-real-model-http-gpt2-20260909` crosses the real HTTP boundary with
  streamed tokens, actual arrival times, bounded admission, and cancellation.
  All 16 requests per mode match individual library generation. Completion p95:
  2,519.89 ms serial eager, 942.51 ms eager microbatch, 640.13 ms SDPA microbatch.
  The separate overload probe rejects 14 requests; in-flight cancellation stops
  token delivery before completion. These are small-sample loopback results.
- All three reports pass `verify_real_model_system.py`, including raw timing,
  output, accounting, source snapshot, and trace-hash checks where applicable.
  Seventeen local tests pass. The workbench verifier passes with the decision
  artifact linked into attention, serving, and profiling recommendations.
- The generated [decision page](../site/real-model-inference-decision.html) is
  backed by `analysis/real-model-inference-decision.json` and regenerated by
  `scripts/build_real_model_decision.py`.

## Counterbalanced serving and independent replay

`colab-real-model-http-repeated-gpt2-20260909` executes four modes over four
rounds, rotating the order so every mode occupies each position once. Each
mode/round serves 16 actual HTTP requests. The optimized custom paged path
executes 720 attention calls in each round; numerical outputs, actual KV-cache
bytes, queue accounting, and client timing summaries pass the verifier.

`colab-real-model-http-replay-gpt2-20260909` repeats the same experiment in a
distinct Colab session from the captured source archive in a temporary folder.
All 44 required dependency versions match, source hashes match, and generated
reference tokens match. Both sessions pass all 512 main-load requests in total.
The archive includes nine local source files, a source manifest, and the
recorded package versions. This proves fresh-session, dependency-checked replay;
it is not a claim that every arbitrary machine can install that CUDA stack.

Median **per-round completion p95**, not pooled request p95:

| Mode | Original session | Fresh-session replay |
| --- | ---: | ---: |
| Serial eager | 2,580.44 ms | 2,710.74 ms |
| Eager microbatch | 728.43 ms | 699.02 ms |
| SDPA microbatch | 695.68 ms | 676.04 ms |
| Optimized paged microbatch | 857.46 ms | 718.15 ms |

The selected conservative path is native eager microbatching: batch limit 4,
queue limit 32, 5 ms window, and 16 generated tokens. It beats serial eager in
every recorded round. SDPA and custom paging remain available experiments;
neither establishes an advantage over eager batching in every round.

Start the selected endpoint with
`python3 batch1-decode-vertical-slice/serve_real_model.py --backend eager`.
The source archive replays the full benchmark via
`python run_real_model_http_repeated.py --output-dir reports` in a matching
environment. `replay_real_model_bundle.py` checks source and dependency identity
before executing that archive.

The six-gate audit is generated by `verify_real_model_goal.py` into
`analysis/real-model-goal-audit.json`; consult its status and individual checks.
This bounded slice does not close the full advanced curriculum goal.

Extensions beyond the recorded protocol remain open: longer generations,
sustained arrivals, production quality/capacity, multi-GPU, and portability.
Mixed-batch cancellation retains slots until the batch ends; its peer-isolation
contract is CPU-tested, while the recorded GPU cancellation probe is singleton.

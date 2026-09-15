# Execution-in-the-Loop LLM Verification Agent

## Meaty end-to-end goal

Turn the certified verification workflow into a model-agnostic LLM agent that can inspect structured specification, RTL, testbench, log, waveform, and dependency-cone evidence; propose a diagnosis and next discriminating test; generate a review-only repair; execute only through deterministic open-source tools; compare an identical-scope retest; and package the complete trajectory for human and adversarial review.

The agent must be useful without being trusted by default. Every model output is typed, source-revision-bound, evidence-linked, forbidden from asserting closure, and checked by deterministic validators. An adversarial judge challenges unsupported signals, stale evidence, scope changes, vacuous properties, and claims that exceed the observed tool result. Local/open models and the deterministic reference agent must share the same contract and be compared on the same failures.

## Definition of done

One benchmark command must run a matched set of failures through the deterministic reference agent and an interchangeable LLM backend, execute proposed next tests and approved repairs through the open-source checker, reject unsafe or ungrounded trajectories, measure triage latency/manual actions/evidence completeness/diagnosis usefulness/repair success/closure integrity, and emit replayable traces plus a signed comparison report.

The result demonstrates an advanced LLM verification workflow; it does not claim exhaustive coverage, formal completeness, silicon correctness, or customer ROI.

## Current executable closure path

The provider-free closure state machine is now exercised by:

```bash
python3 scripts/run_agentic_hardware_closure.py \
  --output /tmp/agentic-hardware-loop
```

This command runs the 11-case diagnosis benchmark, bounded primary repair,
held-out temporal repair, independent SHA-256 package verification, and stops
at `review_required`. With explicit human approval it applies both repairs only
to disposable copies and can hash-link the primary repaired source to an
imported clean RTL-to-GDS/LVS handoff. The independent checker is
`scripts/check_agentic_hardware_closure.py`.

The local deterministic fixture path is the reproducibility baseline. Real
model quality is supported only by a separately verified model artifact; the
current CPU-only local checkpoints are too slow for bounded acceptance and are
classified as blocked on timeout rather than promoted.

## First slice

Establish the provider-neutral agent trajectory contract and run it against the existing 11-fault reference corpus. The first artifact records typed proposals, evidence bindings, deterministic rejection cases, and baseline metrics before any external model is configured.

The first slice is implemented by `python3 scripts/run_llm_agent_benchmark.py`: all 11 reference failures produce grounded, review-required diagnosis proposals; both interchangeable model backends are invoked for every case when configured; and three unsafe trajectories (forbidden closure claim, missing evidence, unsupported kind) are rejected. The resulting `.artifacts/llm-agent-benchmark.json` records per-case model status, grounding, and errors and is included in the commercial handoff inventory.

To exercise the complete local transport without proprietary infrastructure, run `VERIFICATION_LLM_COMMAND='python3 scripts/mock_llm_backend.py' python3 scripts/run_llm_agent_benchmark.py --output .artifacts/llm-agent-benchmark-mock.json`. This fixture produced 11/11 available, grounded, diagnosis-matching proposals and 11/11 deterministic passed retests. Those numbers validate the transport and measurement harness; they are not a claim about an actual language model.

The cached Hugging Face backend is available through `scripts/hf_llm_backend.py` and is intentionally bounded by `VERIFICATION_HF_MAX_NEW_TOKENS` (default 256). It now shares the typed request contract with the resident batch worker, including repair, assertion, and lemma roles; when no model path is configured it resolves known local hub snapshots before falling back to the model identifier. CPU inference is currently slow enough that model latency and timeout behavior must be measured before enabling it for a full corpus run; a blocked or malformed response remains a valid, auditable outcome.

For runtimes that can keep weights resident, `VERIFICATION_LLM_BATCH_COMMAND` uses the JSONL worker contract (`scripts/hf_llm_batch_backend.py`) and serves all cases from one process. The batch harness was exercised with the local fixture at 11/11 available and grounded.

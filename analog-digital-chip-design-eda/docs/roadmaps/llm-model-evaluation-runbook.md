# Real-model evaluation runbook

This runbook evaluates a local/open model under the execution-in-the-loop contract. It does not require a proprietary provider.

## Prepare

Use a host with a resident local model worker and set:

```bash
export VERIFICATION_LLM_BATCH_COMMAND='python3 scripts/hf_llm_batch_backend.py'
export VERIFICATION_HF_MODEL=/models/smollm2-360m-instruct
export VERIFICATION_HF_MAX_NEW_TOKENS=64
```

The worker must read one JSON request per line and emit one proposal JSON object per line. Every proposal is validated and adversarially reviewed before it can contribute to a metric.

## Run

```bash
python3 scripts/run_llm_agent_benchmark.py \
  --output .artifacts/llm-agent-benchmark-real-model.json
python3 scripts/verify_commercial_handoff_manifest.py \
  .artifacts/commercial-handoff-manifest.json
```

The benchmark uses the same 11 failures and deterministic checker execution as the reference baseline. It records availability, latency, evidence grounding, diagnosis match, blocked responses, and adversarial acceptance per case.

For the GPU-backed path, use the checked-in Colab transport:

```bash
COLAB_SESSION_NAME=aimc-llm-agent \
COLAB_GPU_TYPE=T4 \
COLAB_MODEL_ID=Qwen/Qwen2.5-0.5B-Instruct \
COLAB_ASSIGN_RETRIES=3 \
COLAB_ASSIGN_BACKOFF_SECONDS=20 \
bash colab/run_llm_agent_benchmark_local.sh
```

The runner creates a fresh temporary Colab session, uploads source only,
downloads model weights inside that session, and retrieves the verified model
report. Feed that report into
`scripts/run_agentic_hardware_closure.py --model-report <report>` to replay
the repair, held-out formal, physical-flow, and release-manifest gates. The
Colab report is a model-quality input; it never authorizes an RTL mutation or
release by itself.
The launcher retries session assignment a bounded number of times and records
all attempts when Colab is unavailable. Use `COLAB_ASSIGN_RETRIES=1` and
`COLAB_ASSIGN_BACKOFF_SECONDS=0` to disable retry delay.

For an older downloaded report produced before runtime provenance was embedded,
attach the independently downloaded Colab receipt with:

```bash
python3 scripts/attest_colab_benchmark.py \
  <benchmark-report.json> \
  <aimc-llm-agent-colab-summary.json> \
  <attested-benchmark-report.json>
```

The attestation requires a passed Colab summary, a model identity, and a GPU
identity; it records both source digests and is then accepted by the closure
orchestrator's `--require-real-model` gate.

## Acceptance gates

Report model quality only when all 11 cases have a terminal backend result, every available proposal is adversarially accepted, and deterministic retests complete at identical scope. Publish diagnosis-match rate, grounding rate, blocked rate, p50/p95 latency, and human-review count. A blocked, malformed, stale, or scope-escaping proposal is a failed trajectory and must remain visible.

Do not claim exhaustive coverage, formal completeness, silicon correctness, customer ROI, or production readiness from this benchmark. The deterministic reference and fixture results validate the harness; only the real-model artifact supports a real-model quality statement.
